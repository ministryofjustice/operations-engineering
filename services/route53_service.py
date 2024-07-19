from dataclasses import dataclass
import boto3


@dataclass
class HostedZoneModel:
    name: str


class Route53Service:
    def __init__(self, profile: str) -> None:
        session = boto3.Session(profile_name=profile)
        self.client = session.client("route53")

    def get_route53_hosted_zones(self) -> list[HostedZoneModel]:
        response = self.client.list_hosted_zones(MaxItems="1")

        hosted_zones: list[HostedZoneModel] = []
        for zone in response["HostedZones"]:
            hosted_zones.append(HostedZoneModel(name=zone["Name"]))

        return hosted_zones
