import os
import unittest
from datetime import date
import pandas as pd
from pandas.testing import assert_frame_equal

from bin import support_stats_reporting

from services.github_service import GithubService
from services.slack_service import SlackService


class TestSupportStatsReporting(unittest.TestCase):
    # First test - test create dataframe from csv happy path
    # Pass the filename and create the dataframe (use a test csv)
    # Unhappy path - what could go wrong - filename does not exist
    #

    def test_csv_exists(directory, filename):
        filepath = os.path.join(directory, filename)
        return os.path.exists(filepath)
        
    def test_create_dataframe_from_csv_returns_dataframe(self):

        filepath = "test/test_bin/fixtures/test_support_stats.csv"
        test_dataframe = support_stats_reporting.create_dataframe_from_csv(filepath)
        print(test_dataframe.tail())

    

    # def test_column_names(self):
    #     dataframe = pd.DataFrame()
    #     self.assertTrue(
    #         dataframe.columns,
    #         {"Type", "Action", "Date"},
    #     )

    # def test_type(self):
    #     dataframe = pd.DataFrame()
    #     self.assertEqual(dataframe["Type"], str)

    # def test_action(self):
    #     dataframe = pd.DataFrame()
    #     self.assertEqual(dataframe["Action"], str)

    # def test_type(self):
    #     dataframe = pd.DataFrame()
    #     self.assertEqual(dataframe["Date"], date)


class TestSupportStatsReportingGetEnvironmentVariables(unittest.TestCase):
    def test_raises_error_when_no_environment_variables_provided(self):
        self.assertRaises(ValueError, support_stats_reporting.get_environment_variables)


if __name__ == "__main__":
    unittest.main()
