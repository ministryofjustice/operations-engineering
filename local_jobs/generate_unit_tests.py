import os
import subprocess
import re
from local_jobs.prompt_template import PROMPT_TEMPLATE
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
        return [file for file in result.stdout.split("\n") if file.split("/")[0] == "services" or file.split("/")[0] == "bin"]
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

def diff_remove_deletions(diff):
    return "".join([line for line in re.split(r'(?<=\n)', diff) if line != "" and line[0] != "-"])

def diff_remove_plus_signs(diff):
    return "".join([line[1:] if line != "" and line[0] == "+" else line for line in re.split(r'(?<=\n)', diff)])

def diff_remove_metadata(diff):
    return diff.split("@@")[2]

def process_diff(diff):
    remove_metadata = diff_remove_metadata(diff)
    split_on_functions = re.split(r'(?=def\s)', remove_metadata)

    # Extract contextual data
    context = ""
    if "def" not in split_on_functions[0]:
        context += split_on_functions[0]
    # Everything before the first function, such as imports and class definition
    context = context + "".join([function for function in split_on_functions if "__init__" in function])
    # Add the class generator function to the context
    context = diff_remove_deletions(diff_remove_plus_signs(context))
    # remove any deletions and plus signs from the context

    functions = [function for function in split_on_functions if "__init__" not in function and "def" in function]
    # All functions excluding class generator

    modified_functions = []
    for function in functions:
        for line in function.split("\n"):
            if line.strip(" ") not in ["", "+", "-"] and (line[0] == "+" or line[0] == "-"):
                modified_functions.append(function)
                break
    # find functions which have been modified/added

    modified_functions = diff_remove_plus_signs(diff_remove_deletions("".join(modified_functions)))
    # remove deletions and plus signs from modified functions

    return {'context': context, 'modified_functions': modified_functions}

def get_modified_functions(path):
    diff = get_file_diff(path)
    modified_functions = process_diff(diff)

    return modified_functions

def build_prompt(code_to_test):
    return PROMPT_TEMPLATE.format(context=code_to_test['context'], modified_functions=code_to_test['modified_functions'])

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
