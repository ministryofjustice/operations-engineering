from dataclasses import dataclass
import boto3


@dataclass
class RecordValueModel:
    value: str


@dataclass
class RecordSetModel:
    name: str
    type: str
    values: list[RecordValueModel]


@dataclass
class HostedZoneModel:
    name: str
    record_sets: list[RecordSetModel]


class Route53Service:
    def __init__(self, profile: str) -> None:
        session = boto3.Session(profile_name=profile)
        self.client = session.client("route53")

    def __get_all_record_sets(self, zone_id: str) -> list[dict]:
        paginator = self.client.get_paginator("list_resource_record_sets")
        paginator_iterator = paginator.paginate(HostedZoneId=zone_id)

        record_sets = []
        for page in paginator_iterator:
            record_sets.extend(page.get("ResourceRecordSets"))
        return record_sets

    def __get_all_hosted_zones(self) -> list[dict]:
        paginator = self.client.get_paginator("list_hosted_zones")
        paginator_iterator = paginator.paginate(
            PaginationConfig={
                "MaxItems": 500,
            }
        )

        record_sets = []
        for page in paginator_iterator:
            record_sets.extend(page.get("HostedZones"))
        return record_sets

    def __get_hosted_zone_record_sets(self, zone_id: str) -> list[RecordSetModel]:
        all_record_sets = self.__get_all_record_sets(zone_id)

        record_sets: list[RecordSetModel] = []
        for record_set in all_record_sets:
            record_set_name = record_set["Name"]
            record_set_type = record_set["Type"]

            record_values: list[RecordValueModel] = []
            resource_records: list[dict[str, str]]
            try:
                resource_records = record_set["ResourceRecords"]
            except KeyError:
                resource_records = []
            for record in resource_records:
                record_values.append(RecordValueModel(value=record["Value"]))

            record_sets.append(
                RecordSetModel(
                    name=record_set_name,
                    type=record_set_type,
                    values=record_values,
                )
            )

        return record_sets

    def get_hosted_zones(self) -> list[HostedZoneModel]:
        all_hosted_zones = self.__get_all_hosted_zones()

        hosted_zones: list[HostedZoneModel] = []
        for zone in all_hosted_zones:
            zone_name = zone["Name"]
            zone_id = zone["Id"]
            hosted_zones.append(
                HostedZoneModel(
                    name=zone_name,
                    record_sets=self.__get_hosted_zone_record_sets(zone_id),
                )
            )
        return hosted_zones
