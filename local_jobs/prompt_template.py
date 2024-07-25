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

The script can be accessed as a module to import classes and functions for testing, as so: 'from {module} import class/function'

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

Do not modify any existing unit tests unless specified.

Please add tests to the current suite for any functions in the script that are missing them.

Please respond with the complete new unit test suite.

For example. given this script:

{example_script}

This is the associated test suite:

{example_test_suite}
""" + COMMON_RULES
