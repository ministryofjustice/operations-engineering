COMMON_RULES = """
Rules:
- Tests must be written in Python using the unittest framework.
- Do not acknowledge the question asked.
- Do not include any extra information.
- Do not explain your answers.
- Only produce the test code, nothing else.
"""

NEW_TEST_SUITE_PROMPT_TEMPLATE = """

Please write a new test suite, using the Python unittest framework, for the provided script:

{file_to_test_content}

For example. given this script:

{example_script}

This is the associated test suite:

{example_test_suite}
""" + COMMON_RULES

MODIFY_TEST_SUITE_PROMPT_TEMPLATE = """

This a a python script:

{file_to_test_content}

This is the current unit test suite for this script:

{unit_test_file_content}

Please update the unit tests for the following functions which have been recently modified:
{modified_function_names}

Please add tests for any functions in the script that are missing them.

For example. given this script:

{example_script}

This is the associated test suite:

{example_test_suite}
""" + COMMON_RULES
