PROMPT_TEMPLATE = """

This a a python script:

{file_to_test_content}

This is the current unit test suite for this script:

{unit_test_file_content}

Please create or update the tests in the test suite provided with new tests for the following functions that have been recently created or modified:
{modified_function_names}

Rules:
- Tests must be written in Python using the unittest framework
"""
