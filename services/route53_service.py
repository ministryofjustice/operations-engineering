from dataclasses import dataclass
import boto3


@dataclass
class RecordModel:
    value: str


@dataclass
class RecordSetModel:
    name: str
    type: str
    records: list[RecordModel]


@dataclass
class HostedZoneModel:
    name: str
    record_sets: list[RecordSetModel]


class Route53Service:
    def __init__(self, profile: str) -> None:
        session = boto3.Session(profile_name=profile)
        self.client = session.client("route53")

    def __get_hosted_zone_record_sets(self, zone_id: str):
        response = self.client.list_resource_record_sets(HostedZoneId=zone_id)

        record_sets: list[RecordSetModel] = []
        for record_set in response["ResourceRecordSets"]:
            record_set_name = record_set["Name"]
            record_set_type = record_set["Type"]

            records: list[RecordModel] = []
            for record in record_set.get("ResourceRecords", []):
                records.append(RecordModel(value=record["Value"]))

            record_sets.append(
                RecordSetModel(
                    name=record_set_name,
                    type=record_set_type,
                    records=records,
                )
            )

        return record_sets

    def get_hosted_zones(self) -> list[HostedZoneModel]:
        response = self.client.list_hosted_zones(MaxItems="1")

        hosted_zones: list[HostedZoneModel] = []
        for zone in response["HostedZones"]:
            zone_name = zone["Name"]
            zone_id = zone["Id"]
            hosted_zones.append(
                HostedZoneModel(
                    name=zone_name,
                    record_sets=self.__get_hosted_zone_record_sets(zone_id),
                )
            )
        return hosted_zones
