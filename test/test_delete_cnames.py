import os
import unittest
from unittest.mock import patch
import boto3
import botocore.session
from botocore.stub import Stubber
from bin import delete_cnames


class TestDeleteCNames(unittest.TestCase):

    response_when_false = {
        "IsTruncated": False,
        "ResourceRecordSets": [],
        "MaxItems": "300"
    }

    expected_params_when_false = {
        "HostedZoneId": "abc",
        "StartRecordName": "some_value",
        "StartRecordType": "CNAME",
        "MaxItems": "400"
    }

    expected_params_when_true = {
        "HostedZoneId": "abc",
        "StartRecordName": "a",
        "StartRecordType": "CNAME",
        "MaxItems": "400"
    }

    expected_cname_to_delete = {
        "Action": "DELETE",
        "ResourceRecordSet": {
            "Name": "abc",
            "Type": "CNAME",
            "TTL": 123,
            "ResourceRecords": [{"Value": "cname_value_comodoca"}],
        },
    }

    @patch.dict(os.environ, {"HOSTED_ZONE_1": "abc"})
    @patch.dict(os.environ, {"HOSTED_ZONE_2": "abc"})
    @patch.object(boto3, "client")
    def test_main_smoke_test(self, mock_client):
        stubbed_client = botocore.session.get_session().create_client('route53')
        stubber = Stubber(stubbed_client)
        response = {
            "IsTruncated": False,
            "ResourceRecordSets": [],
            "MaxItems": "300"
        }
        mock_client.return_value = stubbed_client

        stubber.add_response('list_resource_record_sets',
                             response, self.expected_params_when_true)
        stubber.add_response('list_resource_record_sets',
                             response, self.expected_params_when_true)
        stubber.activate()

        delete_cnames.main()

    @patch.dict(os.environ, {"HOSTED_ZONE_2": "123"})
    def test_main_returns_error_when_first_token_is_not_provided(self):
        self.assertRaises(
            ValueError, delete_cnames.main)

    @patch.dict(os.environ, {"HOSTED_ZONE_1": "123"})
    def test_main_returns_error_when_second_token_is_not_provided(self):
        self.assertRaises(
            ValueError, delete_cnames.main)

    @patch.dict(os.environ, {"HOSTED_ZONE_1": "abc"})
    @patch.dict(os.environ, {"HOSTED_ZONE_2": "abc"})
    @patch.object(boto3, "client")
    def test_get_cname_records_to_delete_with_pagination_with_no_cname_records(self, mock_client):
        stubbed_client = botocore.session.get_session().create_client('route53')
        stubber = Stubber(stubbed_client)
        response_when_true = {
            "IsTruncated": True,
            "ResourceRecordSets": [],
            "MaxItems": "300",
            "NextRecordName": "some_value",
        }

        mock_client.return_value = stubbed_client

        stubber.add_response('list_resource_record_sets',
                             response_when_true, self.expected_params_when_true)
        stubber.add_response('list_resource_record_sets',
                             self.response_when_false, self.expected_params_when_false)
        stubber.activate()

        self.assertEqual(delete_cnames.get_cname_records_to_delete(
            stubbed_client, "abc"), [])

    @patch.object(boto3, "client")
    def test_get_cname_records_to_delete_with_pagination_when_cname_records_exist_but_not_ours(self, mock_client):
        stubbed_client = botocore.session.get_session().create_client('route53')
        stubber = Stubber(stubbed_client)
        response_when_true = {
            "IsTruncated": True,
            "ResourceRecordSets": [
                {
                    "Name": "abc",
                    "Type": "CNAME",
                    "ResourceRecords": [
                        {
                            "Value": "some_cname_value"
                        }
                    ]
                }
            ],
            "MaxItems": "300",
            "NextRecordName": "some_value",
        }

        mock_client.return_value = stubbed_client

        stubber.add_response('list_resource_record_sets',
                             response_when_true, self.expected_params_when_true)
        stubber.add_response('list_resource_record_sets',
                             self.response_when_false, self.expected_params_when_false)
        stubber.activate()

        self.assertEqual(delete_cnames.get_cname_records_to_delete(
            stubbed_client, "abc"), [])

    @patch.object(boto3, "client")
    def test_get_cname_records_to_delete_with_pagination_when_cname_records_exist(self, mock_client):
        stubbed_client = botocore.session.get_session().create_client('route53')
        stubber = Stubber(stubbed_client)
        response_when_true = {
            "IsTruncated": True,
            "ResourceRecordSets": [
                {
                    "Name": "abc",
                    "Type": "CNAME",
                    "TTL": 123,
                    "ResourceRecords": [
                        {
                            "Value": "cname_value_comodoca"
                        }
                    ]
                },
                {
                    "Name": "abc",
                    "Type": "CNAME",
                    "TTL": 123,
                    "ResourceRecords": [
                        {
                            "Value": "cname_value_sectigo"
                        }
                    ]
                }
            ],
            "MaxItems": "300",
            "NextRecordName": "some_value",
        }

        mock_client.return_value = stubbed_client

        stubber.add_response('list_resource_record_sets',
                             response_when_true, self.expected_params_when_true)
        stubber.add_response('list_resource_record_sets',
                             self.response_when_false, self.expected_params_when_false)
        stubber.activate()

        records_to_delete = delete_cnames.get_cname_records_to_delete(
            stubbed_client, "abc")
        self.assertEqual(len(records_to_delete), 2)

    def test_create_delete_cname_record(self):
        cname_input = {
            "Name": "abc",
            "Type": "CNAME",
            "TTL": 123,
            "ResourceRecords": [
                {
                    "Value": "cname_value_comodoca"
                }
            ]
        }

        self.assertEqual(delete_cnames.create_delete_cname_record(
            cname_input), self.expected_cname_to_delete)

    @patch.object(boto3, "client")
    def test_delete_cname_records(self, mock_client):
        stubbed_client = botocore.session.get_session().create_client('route53')
        stubber = Stubber(stubbed_client)
        expected_params = {
            "ChangeBatch": {
                "Changes": [self.expected_cname_to_delete]
            },
            "HostedZoneId": "abc",
        }

        response = {
            "ResponseMetadata": {
                'RequestId': '1234',
                "HTTPStatusCode": 200,
            },
            "ChangeInfo": {
                "Status": "Pending",
                "Id": "",
                "SubmittedAt": "2022-01-01"
            }
        }

        stubber.add_response('change_resource_record_sets',
                             response, expected_params)
        stubber.activate()
        mock_client.return_value = stubbed_client

        delete_cnames.delete_cname_records(
            stubbed_client, [self.expected_cname_to_delete], "abc")


if __name__ == "__main__":
    unittest.main()
