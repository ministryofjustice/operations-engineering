import argparse
import os
import subprocess
import re
from services.bedrock_service import BedrockService

def parse_args():
    """
    Parse command line arguments.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--modified-files", type=str, required=True, help="Space separated list of modified files in the bin and services directories"
    )

    return parser.parse_args()

def validate_source_file_path(source_file_path):
    if not os.path.isfile(source_file_path):
        raise FileNotFoundError(f"Source file not found at {source_file_path}")

def get_file_diff(path):
    try:
        result = subprocess.run(
            ['git', 'diff', f'main...automatic-unit-test-generation', '--function-context', path],
            check=True,
            text=True,
            capture_output=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f'Error: {e.stderr}')
        return None

def process_diff(diff):
    lines = diff.split("\n")
    remove_metadata = lines[6:]
    string_with_metadata_removed = "\n".join(remove_metadata)
    functions = re.split(r'(?=def\s)', string_with_metadata_removed)

    modified_functions = []
    for function in functions:
        for line in function.split("\n"):
            if line.strip(" ") not in ["", "+", "-"] and (line[0] == "+" or line[0] == "-"):
                modified_functions.append(function)
                break

    string_of_modified_functions = "\n".join(modified_functions)

    remove_deletions = "\n".join([line for line in string_of_modified_functions.split("\n") if line != "" and line[0] != "-"])

    remove_addition_symbols = "\n".join([line[1:] if line != "" and line[0] == "+" else line for line in remove_deletions.split("\n")])

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
    args = parse_args()
    modified_files = args.modified_files.split(" ")
    for path in modified_files:
        generate_tests(path)


if __name__ == "__main__":
    main()
