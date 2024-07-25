import os
import subprocess
import re
from local_jobs.prompt_template import NEW_TEST_SUITE_PROMPT_TEMPLATE, MODIFY_TEST_SUITE_PROMPT_TEMPLATE
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

def validate_test_file_path(path):
    return os.path.isfile(path)

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
    match = re.search(r'\s*def\s+([a-zA-Z_][a-zA-Z_0-9]*)\s*\(', function_str)
    if match:
        return match.group(1)
    else:
        return None

def find_new_functions(diff):
    return [extract_function_name(line) for line in diff.split("\n") if "def" in line and line.startswith("+") and "__init__" not in line]

def get_modified_function_names_from_diff(diff):
    functions = [function for function in re.split(r'(?=def\s)', diff) if "def" in function and "__init__" not in function]

    modified_function_names = []
    for function in functions:
        for line in function.split("\n"):
            if line.strip(" ") not in ["", "+", "-"] and line.startswith("+") or line.startswith("-"):
                modified_function_names.append(extract_function_name(function))
                break

    new_function_names = find_new_functions(diff)

    return ", ".join(list(set(modified_function_names).difference(new_function_names)))

def get_modified_function_names(path):
    diff = get_file_diff(path)
    modified_function_names = get_modified_function_names_from_diff(diff)

    return modified_function_names

def build_prompt(path, template="new_test_suite", test_path="", modified_function_names=[]):
    file_to_test_content = read_file_contents(path)
    example_script = read_file_contents("services/cloudtrail_service.py")
    example_test_suite = read_file_contents("test/test_services/test_cloudtrail_service.py")

    if template == "new_test_suite":
        return NEW_TEST_SUITE_PROMPT_TEMPLATE.format(
        file_to_test_content=file_to_test_content,
        example_script=example_script,
        example_test_suite=example_test_suite
    )
    elif template == "modify_test_suite":
        unit_test_file_content = read_file_contents(test_path)

        return MODIFY_TEST_SUITE_PROMPT_TEMPLATE.format(
            file_to_test_content=file_to_test_content,
            unit_test_file_content=unit_test_file_content,
            modified_function_names=modified_function_names,
            example_script=example_script,
            example_test_suite=example_test_suite
        )

def write_file_contents(path, generated_unit_tests):
    if not os.path.isfile(path):
        with open(path, "w") as file:
            file.write(generated_unit_tests)
    else:
        with open(path, "a") as file:
            file.write("\n\n" + generated_unit_tests)

def read_file_contents(path):
    if os.path.isfile(path):
        with open(path, 'r') as file:
            return file.read()
    else:
        return ""

def generate_tests(path):
    print(f"Generating unit tests for {path}")

    test_path = f"test/test_{path.split('/')[0]}/test_{path.split('/')[1]}"

    validate_source_file_path(path)

    if validate_test_file_path(test_path):
        template = "modify_test_suite"
        modified_function_names = get_modified_function_names(path)
        prompt = build_prompt(path, template, test_path, modified_function_names)
    else:
        prompt = build_prompt(path)

    bedrock_service = BedrockService()
    model = "llama"

    generated_unit_tests = bedrock_service.request_model_response_from_bedrock(prompt, model)

    print(generated_unit_tests)

    write_file_contents(test_path, generated_unit_tests)

    print("Unit test generation complete")

def main():
    modified_files = get_modified_paths()
    for path in modified_files:
        generate_tests(path)

if __name__ == "__main__":
    main()
