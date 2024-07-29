COMMON_RULES = """
Rules:
- Tests must be written in Python using the unittest framework.
- Do not acknowledge the question asked.
- Do not include any extra information.
- Do not explain your answers.
- Only produce the test code, nothing else.
- Make sure that you are importing classes and function into the test script in the correct way:
"from services.my_service import MyService" for services and "from bin.my_job import my_function" for bin jobs.
- Do not include any markdown in the output e.g. ```python something ```
- Ensure constants are correctly imported: "from config.constants import MY_CONSTANT"
"""

NEW_TEST_SUITE_PROMPT_TEMPLATE = """

Please write a new test suite, using the Python unittest framework, for the provided script:

{file_to_test_content}

Classes and functions should be imported into the test script from the following module reference: {module}

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

Please add tests to the current suite for functions in the script do not have unit tests.

Do not create additional unit tests for functions that are already associated with unit tests.

Please respond with the complete new unit test suite.

For example. given this script:

{example_script}

This is the associated test suite:

{example_test_suite}
""" + COMMON_RULES

FAILED_TESTS_PROMPT_TEMPLATE = """
This is the script that I am testing:

{file_to_test_content}

This is the current unit test suite for this script:

{unit_test_file_content}

These are the current unit test failures:
{failed_tests}

Please amend the failing tests so that they pass and return the new test suite.

Use mock_response.__getitem__.return_value to mock response["body"].
""" + COMMON_RULES
