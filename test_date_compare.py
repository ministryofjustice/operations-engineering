import os
import unittest
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from pytz import timezone

from unittest.mock import MagicMock, patch
from freezegun import freeze_time

from bin import archive_repositories


class TestDateCompare(unittest.TestCase):

    def test_tz_aware_compare_naive_raises_type_error(self):
        with self.assertRaises(TypeError):
            tz_aware = datetime(2020, 5, 17, tzinfo=timezone('Europe/London'))
            tz_naive = datetime.now() - relativedelta(days=0, months=6, years=1)
            tz_aware < tz_naive

    def test_aware_datetime_tzinfo_is_not_none(self):
        tzinfo_aware = datetime(
            2020, 5, 17, tzinfo=timezone('Europe/London')).tzinfo
        print(tzinfo_aware)
        message = "Timezone aware datetime timezone information is None."
        self.assertIsNotNone(tzinfo_aware, message)

    def test_naive_datetime_tzinfo_is_none(self):
        tzinfo_aware = datetime(2020, 5, 17).tzinfo
        message = "Timezone naive datetime timezone is not None."
        self.assertIsNone(tzinfo_aware, message)

    def test_tzinfo_not_equal_when_set_aware(self):
        tzinfo_aware = datetime(
            2020, 5, 17, tzinfo=timezone('Europe/London')).tzinfo
        tzinfo_naive = datetime(2020, 5, 17).tzinfo
        message = "Timezone information is not unequal."
        self.assertNotEqual(tzinfo_aware, tzinfo_naive, message)

    def test_tzinfo_equal_when_aware_set_to_none(self):
        removed_tzinfo_aware = datetime(2020, 5, 17, tzinfo=timezone(
            'Europe/London')).replace(tzinfo=None).tzinfo
        tzinfo_naive = datetime(2020, 5, 17).tzinfo
        message = "Timezone information is not equal."
        self.assertEqual(removed_tzinfo_aware, tzinfo_naive, message)

    def test_tzinfo_not_equal(self):
        tz_aware = datetime(
            2020, 5, 17, tzinfo=timezone('Europe/London')).tzinfo
        tz_naive = (datetime.now() -
                    relativedelta(days=0, months=6, years=1)).tzinfo
        message = "First value and second value are not unequal."
        self.assertNotEqual(tz_aware, tz_naive, message)

    def test_tzinfo_equal_when_both_set_to_none(self):
        removed_tzinfo_aware = datetime(2020, 5, 17, tzinfo=timezone(
            'Europe/London')).replace(tzinfo=None).tzinfo
        removed_tzinfo_naive = (datetime.now(
        ) - relativedelta(days=0, months=6, years=1)).replace(tzinfo=None).tzinfo
        message = "Timezone information is not equal."
        self.assertEqual(removed_tzinfo_aware, removed_tzinfo_naive, message)

    def test_removing_tzinfo_ensures_comparable(self):
        removed_tzinfo_aware = datetime(
            2020, 5, 17, tzinfo=timezone('Europe/London')).replace(tzinfo=None)
        removed_tzinfo_naive = (
            datetime.now() - relativedelta(days=0, months=6, years=1)).replace(tzinfo=None)
        message = "First value is not less that second value."
        self.assertLess(removed_tzinfo_aware, removed_tzinfo_naive, message)


if __name__ == "__main__":
    unittest.main()
