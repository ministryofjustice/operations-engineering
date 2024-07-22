from config.logging_config import logging
import json
from services.route53_service import (
    HostedZoneModel,
    RecordSetModel,
    RecordValueModel,
    Route53Service,
)
from dataclasses import dataclass, field


@dataclass
class Delegations:
    type: str
    name: str
    all: list = field(default_factory=list)
    to_dsd: list = field(default_factory=list)
    to_cloud_platform: list = field(default_factory=list)
    to_unknown: list = field(default_factory=list)


def __flatten_record_value(record_values: list[RecordValueModel]) -> list[str]:
    return [record.value for record in record_values]


def __is_delegated_to_hosted_zones(
    hosted_zones: list[HostedZoneModel], name_server_record: RecordSetModel
) -> bool:
    for hosted_zone in hosted_zones:
        if hosted_zone.name != name_server_record.name:
            continue

        hosted_zones_name_servers: RecordSetModel | bool = False

        for record_set in hosted_zone.record_sets:
            if record_set.name == hosted_zone.name and record_set.type == "NS":
                hosted_zones_name_servers = record_set

        if not hosted_zones_name_servers:
            logging.warn(f"HostedZone [ ${hosted_zone.name} ] does not have NS record")
            continue

        name_servers_to_check = __flatten_record_value(name_server_record.values)
        hosted_zone_name_servers_to_check = __flatten_record_value(
            hosted_zones_name_servers and hosted_zones_name_servers.values
        )
        name_servers_to_check.sort()
        hosted_zone_name_servers_to_check.sort()

        if name_servers_to_check == hosted_zone_name_servers_to_check:
            return True

    return False


def main():
    dsd_route53_service = Route53Service(profile="dsd_route53_read")
    cloud_platform_route53_service = Route53Service(
        profile="cloud_platform_route53_read"
    )

    dsd_hosted_zones: list[HostedZoneModel] = dsd_route53_service.get_hosted_zones()
    cloud_platform_hosted_zones: list[HostedZoneModel] = (
        cloud_platform_route53_service.get_hosted_zones()
    )

    dsd_delegations = Delegations(type="ACCOUNT", name="DSD")
    delegations: list[Delegations] = [dsd_delegations]

    for hosted_zone in dsd_hosted_zones:
        hosted_zone_delegations = Delegations(
            type="HOSTED_ZONES", name=f"DSD - {hosted_zone.name}"
        )
        for record_set in hosted_zone.record_sets:
            is_delegation = (
                True
                if record_set.type == "NS" and record_set.name != hosted_zone.name
                else False
            )

            if not is_delegation:
                continue

            found_delegation = False
            hosted_zone_delegations.all.append(record_set.name)
            dsd_delegations.all.append(record_set.name)

            if __is_delegated_to_hosted_zones(dsd_hosted_zones, record_set):
                hosted_zone_delegations.to_dsd.append(record_set.name)
                dsd_delegations.to_dsd.append(record_set.name)
                found_delegation = True

            if __is_delegated_to_hosted_zones(cloud_platform_hosted_zones, record_set):
                hosted_zone_delegations.to_cloud_platform.append(record_set.name)
                dsd_delegations.to_cloud_platform.append(record_set.name)
                found_delegation = True

            if not found_delegation:
                hosted_zone_delegations.to_unknown.append(record_set.name)
                dsd_delegations.to_unknown.append(record_set.name)

        delegations.append(hosted_zone_delegations)

    logging.info(
        json.dumps(
            {
                "totals": {
                    "all": len(dsd_delegations.all),
                    "unknownDelegations": len(dsd_delegations.to_unknown),
                    "internalDelegations": len(dsd_delegations.to_dsd),
                    "cloudPlatformDelegations": len(dsd_delegations.to_cloud_platform),
                },
                "delegations": delegations,
            },
            default=lambda o: o.__dict__,
        )
    )


if __name__ == "__main__":
    main()
