import os
import csv
import json
import tempfile
import unittest
from unittest.mock import call, patch, mock_open
from freezegun import freeze_time
from services.route_53_service import Route53Service
from config.constants import NO_ACTIVITY
from moto import mock_aws
import boto3

class TestRoute53Service(unittest.TestCase):

    @mock_aws
    def setUp(self):
        self.route_53_service = Route53Service()
        self.route_53_service.client = boto3.client("route53", region_name="us-west-2")

    @mock_aws
    def test_get_route53_hosted_zones(self):
        zone = self.route_53_service.client.create_hosted_zone(Name="testdns.aws.com.", CallerReference=str(hash("foo")))

        res = self.route_53_service.get_route53_hosted_zones()

        assert res[0] == zone['HostedZone']['Id']

if __name__ == "__main__":
    unittest.main()
