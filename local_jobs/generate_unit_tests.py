import os
import subprocess
import re
from local_jobs.prompt_template import NEW_TEST_SUITE_PROMPT_TEMPLATE, MODIFY_TEST_SUITE_PROMPT_TEMPLATE, FAILED_TESTS_PROMPT_TEMPLATE
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

    filter_out_new_functions = list(set(modified_function_names).difference(new_function_names))

    if len(filter_out_new_functions) > 0:
        return ", ".join(filter_out_new_functions)

    return "No existing functions have been modified."


def get_modified_function_names(path):
    diff = get_file_diff(path)
    modified_function_names = get_modified_function_names_from_diff(diff)

    return modified_function_names


def build_prompt(path, template="new_test_suite", test_path="", modified_function_names="", failed_tests=""):
    file_to_test_content = read_file_contents(path)
    example_script = read_file_contents("services/cloudtrail_service.py")
    example_test_suite = read_file_contents("test/test_services/test_cloudtrail_service.py")
    unit_test_file_content = ""

    if test_path != "":
        unit_test_file_content = read_file_contents(test_path)

    if template == "new_test_suite":
        module = path.replace("/", ".").strip(".py")

        return NEW_TEST_SUITE_PROMPT_TEMPLATE.format(
            module=module,
            file_to_test_content=file_to_test_content,
            example_script=example_script,
            example_test_suite=example_test_suite
        )

    if template == "modify_test_suite":
        return MODIFY_TEST_SUITE_PROMPT_TEMPLATE.format(
            file_to_test_content=file_to_test_content,
            unit_test_file_content=unit_test_file_content,
            modified_function_names=modified_function_names,
            example_script=example_script,
            example_test_suite=example_test_suite
        )

    if template == "failed_tests":
        return FAILED_TESTS_PROMPT_TEMPLATE.format(
            file_to_test_content=file_to_test_content,
            unit_test_file_content=unit_test_file_content,
            failed_tests=failed_tests
        )

    return ""


def write_file_contents(path, generated_unit_tests):
    with open(path, "w", encoding='utf-8') as file:
        file.write(generated_unit_tests)


def read_file_contents(path):
    if os.path.isfile(path):
        with open(path, 'r', encoding='utf-8') as file:
            return file.read()
    else:
        return ""


def run_test_suite(path):
    test_results = subprocess.run(["pipenv", "run", "python", "-m", "unittest", path], capture_output=True, text=True, check=True).stderr

    broken_down_test_results = test_results.split("======================================================================")

    failed_tests = "".join([test for test in broken_down_test_results if "test_raises_error_when_no_github_token" not in test and "fail" in test.lower() or "error" in test.lower()])

    return failed_tests


def generate_tests(prompt, test_path):
    bedrock_service = BedrockService()
    model = "claude"

    # use bedrock to generate unit test skeleton
    generated_unit_tests = bedrock_service.request_model_response_from_bedrock(prompt, model)

    # write tests to file
    write_file_contents(test_path, generated_unit_tests)

    # Run generated unit tests - return any failed tests
    failed_tests = run_test_suite(test_path)

    return failed_tests


def main():
    modified_files = get_modified_paths()

    for path in modified_files:
        print(f"Generating unit tests for {path}")

        test_path = f"test/test_{path.split('/')[0]}/test_{path.split('/')[1]}"

        validate_source_file_path(path)

        # Check if test suite already exists and create prompt
        if validate_test_file_path(test_path):
            template = "modify_test_suite"
            modified_function_names = get_modified_function_names(path)

            prompt = build_prompt(path, template, test_path, modified_function_names)
        else:
            prompt = build_prompt(path)

        test_test_path = "test/ai_test/" + test_path.split("/")[2]

        # generate unit tests for specified path
        failed_tests = generate_tests(prompt, test_test_path)

        max_cycles = 3
        cycles = 1

        # send tests back to AI to correct if there are failures
        while len(failed_tests) > 0 and cycles < max_cycles:
            print(f"Generation {cycles} of the test suite has produced the following errors: {failed_tests}")

            cycles += 1

            print(f"Generating generation {cycles} of the test suite")

            template = "failed_tests"
            prompt = build_prompt(path, template, test_test_path, [], failed_tests)

            failed_tests = generate_tests(prompt, test_test_path)

        print("Unit test generation complete")

        if len(failed_tests) > 0:
            print(f"Final test suite still has failures: {failed_tests}")


if __name__ == "__main__":
    main()
