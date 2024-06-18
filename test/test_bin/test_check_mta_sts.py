import unittest
import boto3
from botocore.exceptions import 
from unittest.mock import patch

import check_mta_sts

class TestCheckMtaSts(unittest.TestCase):
    
    @patch('check_mta_sts.boto3.client')
    def test_s3_initialization(self, mock_client):
        mock_client.return_value =None
        s3 = check_mta_sts.boto3.client('s3',
                                        aws_access_key_id=check_mta_sts.AWS_ACCESS_KEY_ID,
                                        aws_secret_access_key=check_mta_sts.AWS_SECRET_ACCESS_KEY,
                                        aws_session_token=check_mta_sts.AWS_SESSION_TOKEN)
        mock_client.assert_called_once_with('s3',
                                            aws_access_key_id=check_mta_sts.AWS_ACCESS_KEY_ID,
                                            aws_secret_access_key=check_mta_sts.AWS_SECRET_ACCESS_KEY,
                                            aws_session_token=check_mta_sts.AWS_SESSION_TOKEN)
        def test_domains(self):
            expected_domains = ["ccrc.gov.uk",
                                "cjit.gov.uk",
                                "cshrcasework.justice.gov.uk",
                                "devl.justice.gov.uk",
                                "g.justice.gov.uk",
                                "govfsl.com",
                                "hmiprisons.gov.uk",
                                "hmiprobation.gov.uk",
                                "ima-citizensrights.org.uk",
                                "imb.org.uk",
                                "judicialappointments.gov.uk",
                                "judicialconduct.gov.uk",
                                "judicialombudsman.gov.uk",
                                "judiciary.uk",
                                "justice.gov.uk",
                                "lawcommission.gov.uk",
                                "newsletter.ima-citizensrights.org.uk",
                                "obr.uk",
                                "ospt.gov.uk",
                                "ppo.gov.uk",
                                "publicguardian.gov.uk",
                                "sentencingcouncil.gov.uk",
                                "sentencingcouncil.org.uk",
                                "ukgovwales.gov.uk",
                                "victimscommissioner.org.uk",
                                "yjb.gov.uk",
                                "yjbservicespp.yjb.gov.uk",
                                "youthjusticepp.yjb.gov.uk"]
            self.assertEqual(check_mta_sts.domains, expected_domains)
if _name_ == '_main_':
    unittest.main()            


