# pylint: disable=C0411
import unittest
from services.s3_service import S3Service
from unittest.mock import patch
from moto import mock_aws
from bin.check_mta_sts import main, check_mta_sts_domains

class TestMTASTS(unittest.TestCase):
    @mock_aws
    def setUp(self):
        self.s3_service = S3Service("880656497252", "ministryofjustice")

    @mock_aws
    @patch.object(S3Service, "is_well_known_mta_sts_enforce")
    def test_check_mta_sts_with_enforce(self, mock_is_well_known_mta_sts_enforce):
        mock_is_well_known_mta_sts_enforce.return_value = True

        self.assertEqual(len(check_mta_sts_domains(self.s3_service)), 0)

    @mock_aws
    @patch.object(S3Service, "is_well_known_mta_sts_enforce")
    def test_check_mta_sts_without_enforce(self, mock_is_well_known_mta_sts_enforce):
        mock_is_well_known_mta_sts_enforce.side_effect = lambda domain: domain != "yjb.gov.uk"

        self.assertIn("yjb.gov.uk", check_mta_sts_domains(self.s3_service))

    @patch('bin.check_mta_sts.check_mta_sts_domains')
    def test_main_function_with_enforce(self, mock_check_mta_sts_domains):
        main()
        mock_check_mta_sts_domains.assert_called_once()


if __name__ == "__main__":
    unittest.main()
