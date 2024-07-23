import os
import subprocess
import re
from services.bedrock_service import BedrockService

def get_current_branch():
    try:
        result = subprocess.run(
            ['git', 'branch', '--show-current'],
            check=True,
            text=True,
            capture_output=True
        )
        return result.stdout.strip("\n")
    except subprocess.CalledProcessError as e:
        print(f'Error: {e.stderr}')
        return None

def get_modified_files():
    try:
        result = subprocess.run(
            ['git', 'diff', '--name-only', f"main...{get_current_branch()}"],
            check=True,
            text=True,
            capture_output=True
        )
        return [file for file in result.stdout.split("\n") if "services/" in file or "bin/" in file]
    except subprocess.CalledProcessError as e:
        print(f'Error: {e.stderr}')
        return None

def validate_source_file_path(source_file_path):
    if not os.path.isfile(source_file_path):
        raise FileNotFoundError(f"Source file not found at {source_file_path}")

def get_file_diff(path):
    try:
        result = subprocess.run(
            ['git', 'diff', f"main...{get_current_branch()}", '--function-context', path],
            check=True,
            text=True,
            capture_output=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f'Error: {e.stderr}')
        return None

def process_diff(diff):
    remove_metadata = diff.split("\n")[6:]
    functions = re.split(r'(?=def\s)', "\n".join(remove_metadata))

    modified_functions = []
    for function in functions:
        for line in function.split("\n"):
            if line.strip(" ") not in ["", "+", "-"] and (line[0] == "+" or line[0] == "-"):
                modified_functions.append(function)
                break

    remove_deletions = [line for line in "\n".join(modified_functions).split("\n") if line != "" and line[0] != "-"]

    remove_addition_symbols = "\n".join([line[1:] if line != "" and line[0] == "+" else line for line in remove_deletions])

    return remove_addition_symbols

def get_modified_functions(path):
    diff = get_file_diff(path)
    modified_functions = process_diff(diff)

    return modified_functions

def build_prompt(code_to_test):

    template = f"Please generate unit tests using the Python unittest library for the following functions:\n\n{code_to_test}"

    return template

def write_file_contents(path, generated_unit_tests):
    output_path = f"test/test_{path.split('/')[0]}/test_{path.split('/')[1]}"
    if not os.path.isfile(output_path):
        with open(output_path, "w") as file:
            file.write(generated_unit_tests)
    else:
        with open(output_path, "a") as file:
            file.write("\n\n" + generated_unit_tests)

def generate_tests(path):
    print(f"Generating unit tests for {path}")

    validate_source_file_path(path)

    code_to_test = get_modified_functions(path)

    prompt = build_prompt(code_to_test)

    bedrock_service = BedrockService()

    generated_unit_tests = bedrock_service.make_request(prompt)

    write_file_contents(path, generated_unit_tests)

    print("Unit test generation complete")

def main():
    modified_files = get_modified_files()
    for path in modified_files:
        generate_tests(path)


if __name__ == "__main__":
    main()
