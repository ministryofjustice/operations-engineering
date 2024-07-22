import argparse
import os
from services.bedrock_service import BedrockService

def parse_args():
    """
    Parse command line arguments.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source-file-path", required=True, help="Path to the source file."
    )
    parser.add_argument(
        "--test-file-output-path", required=True, help="Path to the output test file."
    )

    return parser.parse_args()

def validate_source_file_path(source_file_path):
    if not os.path.isfile(source_file_path):
        raise FileNotFoundError(f"Source file not found at {source_file_path}")

def read_file_contents(path):
    with open(path, 'r') as file:
        content = file.read()

        return content

def build_prompt(code_to_test):

    template = f"Please generate unit tests using the Python unittest library for the following functions:\n\n{code_to_test}"

    return template

def write_file_contents(path, generated_unit_tests):
    if not os.path.isfile(path):
        with open(path, "w") as file:
            file.write(generated_unit_tests)
    else:
        with open(path, "a") as file:
            file.write("\n\n" + generated_unit_tests)

def generate_tests(args):
    print("Generating unit tests")

    validate_source_file_path(args.source_file_path)

    code_to_test = read_file_contents(args.source_file_path)

    prompt = build_prompt(code_to_test)

    bedrock_service = BedrockService()

    generated_unit_tests = bedrock_service.make_request(prompt)

    write_file_contents(args.test_file_output_path, generated_unit_tests)

    print("Unit test generation complete")

def main():
    args = parse_args()
    generate_tests(args)


if __name__ == "__main__":
    main()
