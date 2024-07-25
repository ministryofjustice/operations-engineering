from typing import Any
import unittest
from unittest.mock import MagicMock, patch, Mock
from bin.dns_delegations_metrics import main
import json


def mock_paginate(results: list[dict[str, Any]]):
    return Mock(paginate=Mock(return_value=[Mock(get=Mock(return_value=results))]))


def mock_boto3_session(side_effects: list):
    return Mock(
        client=Mock(
            return_value=Mock(
                get_paginator=Mock(
                    side_effect=[
                        mock_paginate(side_effect) for side_effect in side_effects
                    ]
                )
            )
        )
    )


@patch("services.route53_service.boto3")
@patch("bin.dns_delegations_metrics.logging")
class TestDnsDelegationsMetricsMain(unittest.TestCase):
    def test_logs_logs_no_delegations_when_no_hosted_zones_returned(
        self, mock_logging: MagicMock, mock_boto3: MagicMock
    ):
        mock_boto3.Session.return_value = MagicMock()
        main()
        mock_logging.info.assert_called_with(json.dumps({"delegations": []}))

    def test_logs_delegations_that_cannot_be_matched_as_unknown(
        self, mock_logging: MagicMock, mock_boto3: MagicMock
    ):
        mock_dsd_hosted_zones = [{"Name": "justice.gov.uk", "Id": "1"}]
        mock_dsd_records = [{"Name": "test.justice.gov.uk", "Type": "NS"}]
        mock_cp_hosted_zones = [{"Name": "cp.justice.gov.uk", "Id": "2"}]
        mock_cp_records = [{"Name": "test.cp.justice.gov.uk", "Type": "TXT"}]
        mock_boto3.Session.return_value = mock_boto3_session(
            [
                mock_dsd_hosted_zones,
                mock_dsd_records,
                mock_cp_hosted_zones,
                mock_cp_records,
            ]
        )
        main()
        mock_logging.info.assert_called_with(
            json.dumps(
                {
                    "delegations": [
                        {
                            "type": "ACCOUNT",
                            "name": "DSD",
                            "totals": {
                                "all": [1, "100%"],
                                "to_unknown": [1, "100%"],
                                "to_cloud_platform": [0, "0%"],
                                "to_dsd": [0, "0%"],
                            },
                            "all": ["test.justice.gov.uk"],
                            "to_unknown": ["test.justice.gov.uk"],
                            "to_cloud_platform": [],
                            "to_dsd": [],
                        },
                        {
                            "type": "HOSTED_ZONES",
                            "name": "DSD - justice.gov.uk",
                            "totals": {
                                "all": [1, "100%"],
                                "to_unknown": [1, "100%"],
                                "to_cloud_platform": [0, "0%"],
                                "to_dsd": [0, "0%"],
                            },
                            "all": ["test.justice.gov.uk"],
                            "to_unknown": ["test.justice.gov.uk"],
                            "to_cloud_platform": [],
                            "to_dsd": [],
                        },
                    ]
                }
            )
        )

    def test_logs_delegations_to_cloud_platform(
        self, mock_logging: MagicMock, mock_boto3: MagicMock
    ):
        mock_dsd_hosted_zones = [{"Name": "justice.gov.uk", "Id": "1"}]
        mock_dsd_records = [
            {
                "Name": "cp.justice.gov.uk",
                "Type": "NS",
                "ResourceRecords": [{"Value": "ns-1.com"}],
            }
        ]
        mock_cp_hosted_zones = [{"Name": "cp.justice.gov.uk", "Id": "2"}]
        mock_cp_records = [
            {
                "Name": "cp.justice.gov.uk",
                "Type": "NS",
                "ResourceRecords": [{"Value": "ns-1.com"}],
            }
        ]
        mock_boto3.Session.return_value = mock_boto3_session(
            [
                mock_dsd_hosted_zones,
                mock_dsd_records,
                mock_cp_hosted_zones,
                mock_cp_records,
            ]
        )
        main()
        mock_logging.info.assert_called_with(
            json.dumps(
                {
                    "delegations": [
                        {
                            "type": "ACCOUNT",
                            "name": "DSD",
                            "totals": {
                                "all": [1, "100%"],
                                "to_unknown": [0, "0%"],
                                "to_cloud_platform": [1, "100%"],
                                "to_dsd": [0, "0%"],
                            },
                            "all": ["cp.justice.gov.uk"],
                            "to_unknown": [],
                            "to_cloud_platform": ["cp.justice.gov.uk"],
                            "to_dsd": [],
                        },
                        {
                            "type": "HOSTED_ZONES",
                            "name": "DSD - justice.gov.uk",
                            "totals": {
                                "all": [1, "100%"],
                                "to_unknown": [0, "0%"],
                                "to_cloud_platform": [1, "100%"],
                                "to_dsd": [0, "0%"],
                            },
                            "all": ["cp.justice.gov.uk"],
                            "to_unknown": [],
                            "to_cloud_platform": ["cp.justice.gov.uk"],
                            "to_dsd": [],
                        },
                    ]
                }
            )
        )

    def test_logs_delegations_to_dsd(
        self, mock_logging: MagicMock, mock_boto3: MagicMock
    ):
        mock_dsd_hosted_zones = [
            {"Name": "justice.gov.uk", "Id": "1"},
            {"Name": "local.justice.gov.uk", "Id": "2"},
        ]
        mock_dsd_justice_records = [
            {
                "Name": "local.justice.gov.uk",
                "Type": "NS",
                "ResourceRecords": [{"Value": "ns-1.com"}],
            },
        ]
        mock_dsd_local_justice_records = [
            {
                "Name": "local.justice.gov.uk",
                "Type": "NS",
                "ResourceRecords": [{"Value": "ns-1.com"}],
            },
        ]
        mock_cp_hosted_zones = []
        mock_cp_records = []
        mock_boto3.Session.return_value = mock_boto3_session(
            [
                mock_dsd_hosted_zones,
                mock_dsd_justice_records,
                mock_dsd_local_justice_records,
                mock_cp_hosted_zones,
                mock_cp_records,
            ]
        )
        main()
        mock_logging.info.assert_called_with(
            json.dumps(
                {
                    "delegations": [
                        {
                            "type": "ACCOUNT",
                            "name": "DSD",
                            "totals": {
                                "all": [1, "100%"],
                                "to_unknown": [0, "0%"],
                                "to_cloud_platform": [0, "0%"],
                                "to_dsd": [1, "100%"],
                            },
                            "all": ["local.justice.gov.uk"],
                            "to_unknown": [],
                            "to_cloud_platform": [],
                            "to_dsd": ["local.justice.gov.uk"],
                        },
                        {
                            "type": "HOSTED_ZONES",
                            "name": "DSD - justice.gov.uk",
                            "totals": {
                                "all": [1, "100%"],
                                "to_unknown": [0, "0%"],
                                "to_cloud_platform": [0, "0%"],
                                "to_dsd": [1, "100%"],
                            },
                            "all": ["local.justice.gov.uk"],
                            "to_unknown": [],
                            "to_cloud_platform": [],
                            "to_dsd": ["local.justice.gov.uk"],
                        },
                    ]
                }
            )
        )
