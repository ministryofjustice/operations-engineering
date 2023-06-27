import os
import unittest
from unittest.mock import patch
from datetime import datetime
from freezegun import freeze_time
from python.lib.utilities import (
    convert_str_to_bool,
    get_username,
    convert_timestamp_ms_to_date,
    get_future_date,
    get_past_date,
    get_debug_mode,
    convert_string_to_date
)


class TestUtilities(unittest.TestCase):
    def test_convert_str_to_bool(self):
        self.assertEqual(convert_str_to_bool("True"), True)
        self.assertEqual(convert_str_to_bool("true"), True)
        self.assertEqual(convert_str_to_bool("False"), False)
        self.assertEqual(convert_str_to_bool("false"), False)

    def test_get_username(self):
        the_dict = {"username": "some-user"}
        self.assertEqual("some-user", get_username(the_dict))

    def test_convert_string_to_date(self):
        the_date = datetime(2022, 1, 1)
        self.assertEqual(convert_string_to_date("2022-01-01"), the_date)

    def test_convert_timestamp_ms_to_date(self):
        converted_date = convert_timestamp_ms_to_date(1687866802203)
        expected_date = datetime(2023, 6, 27, 12, 53, 22, 203000)
        self.assertEqual(converted_date, expected_date)

    @freeze_time("2023-02-01")
    def test_get_future_date(self):
        future_date = get_future_date(date_days=1, date_months=1, date_years=1)
        expected_date = datetime(2024, 3, 2)
        self.assertEqual(future_date, expected_date)

    @freeze_time("2023-07-10")
    def test_get_past_date(self):
        past_date = get_past_date(date_days=1, date_months=1, date_years=1)
        expected_date = datetime(2022, 6, 9)
        self.assertEqual(past_date, expected_date)

    def test_get_debug_mode_when_not_set(self):
        self.assertEqual(get_debug_mode(), False)

    @patch.dict(os.environ, {"DEBUG_MODE": "false"})
    def test_get_debug_mode_when_false_string(self):
        self.assertEqual(get_debug_mode(), False)

    @patch.dict(os.environ, {"DEBUG_MODE": "true"})
    def test_get_debug_mode_when_true_string(self):
        self.assertEqual(get_debug_mode(), True)


if __name__ == "__main__":
    unittest.main()
