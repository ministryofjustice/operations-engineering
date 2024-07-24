PROMPT_TEMPLATE = """

This a a python script:

{file_to_test_content}

This is the current unit test suite for this script:

{unit_test_file_content}

If there is a pre-existing test suite, please add tests for any functions missing them,
and update the tests for the following functions which have been recently modified:
{modified_function_names}

If no test suite currently exists, please write a new test suite for the provided script.

For example. given this script:

{example_script}

This is the associated test suite:

{example_test_suite}

Rules:
- Tests must be written in Python using the unittest framework.
- Do not acknowledge the question asked.
- Do not include any extra information.
- Do not explain your answers.
- Only produce the test code, nothing else.
"""
