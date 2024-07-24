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

def get_modified_paths():
    try:
        result = subprocess.run(
            ['git', 'diff', '--name-only', "main"],
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
            ['git', 'diff', "main", '--function-context', path],
            check=True,
            text=True,
            capture_output=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f'Error: {e.stderr}')
        return None

def extract_function_name(function_str):
    match = re.match(r'\s*def\s+([a-zA-Z_][a-zA-Z_0-9]*)\s*\(', function_str)
    if match:
        return match.group(1)
    else:
        return None

def get_modified_function_names_from_diff(diff):
    functions = [function for function in re.split(r'(?=def\s)', diff) if "def" in function and "__init__" not in function]

    modified_function_names = []
    for function in functions:
        for line in function.split("\n"):
            if line.strip(" ") not in ["", "+", "-"] and (line[0] == "+" or line[0] == "-"):
                modified_function_names.append(extract_function_name(function))
                break

    return ", ".join(modified_function_names)

def get_modified_function_names(path):
    diff = get_file_diff(path)
    modified_function_names = get_modified_function_names_from_diff(diff)

    return modified_function_names

def build_prompt(file_to_test_content, unit_test_file_content, modified_function_names):
    example_script = read_file_contents("services/cloudtrail_service.py")
    example_test_suite = read_file_contents("test/test_services/test_cloudtrail_service.py")
    return PROMPT_TEMPLATE.format(
        file_to_test_content=file_to_test_content,
        unit_test_file_content=unit_test_file_content,
        modified_function_names=modified_function_names,
        example_script=example_script,
        example_test_suite=example_test_suite
    )

def write_file_contents(path, generated_unit_tests):
    output_path = f"test/test_{path.split('/')[0]}/test_{path.split('/')[1]}"
    if not os.path.isfile(output_path):
        with open(output_path, "w") as file:
            file.write(generated_unit_tests)
    else:
        with open(output_path, "a") as file:
            file.write("\n\n" + generated_unit_tests)

def read_file_contents(path):
    if os.path.isfile(path):
        with open(path, 'r') as file:
            return file.read()
    else:
        return ""

def generate_tests(path):
    print(f"Generating unit tests for {path}")

    validate_source_file_path(path)

    modified_function_names = get_modified_function_names(path)
    file_to_test_content = read_file_contents(path)
    unit_test_file_content = read_file_contents(f"test/test_{path.split('/')[0]}/test_{path.split('/')[1]}")

    prompt = build_prompt(file_to_test_content, unit_test_file_content, modified_function_names)

    bedrock_service = BedrockService()

    generated_unit_tests = bedrock_service.make_request(prompt)

    print(generated_unit_tests)

    # write_file_contents(path, generated_unit_tests)

    print("Unit test generation complete")

def main():
    modified_files = get_modified_paths()
    for path in modified_files:
        generate_tests(path)

if __name__ == "__main__":
    main()
