PROMPT_TEMPLATE = """

This a a python script:

{file_to_test_content}

This is the current unit test suite for this script:

{unit_test_file_content}

Please update the test suite to include new tests, or updated tests if they already exist, for the following functions which have recently been created or modified:
{modified_function_names}

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
