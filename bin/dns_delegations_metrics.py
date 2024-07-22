from config.logging_config import logging
import json
from services.route53_service import (
    HostedZoneModel,
    RecordSetModel,
    RecordValueModel,
    Route53Service,
)


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

    internal_delgations_count = 0
    cloud_platform_delegations_count = 0
    unknown_delegations_count = 0
    total_delegations = 0

    delegated_domains = []
    cloud_platform_delegated_domains = []
    internal_delegated_domains = []
    unkown_delegated_domains = []

    for hosted_zone in dsd_hosted_zones:
        for record_set in hosted_zone.record_sets:
            is_delegation = (
                True
                if record_set.type == "NS" and record_set.name != hosted_zone.name
                else False
            )
            if is_delegation:
                found_delegation = False
                total_delegations += 1
                delegated_domains.append(record_set.name)
                if __is_delegated_to_hosted_zones(dsd_hosted_zones, record_set):
                    internal_delgations_count += 1
                    internal_delegated_domains.append(record_set.name)
                    found_delegation = True

                if __is_delegated_to_hosted_zones(
                    cloud_platform_hosted_zones, record_set
                ):
                    cloud_platform_delegations_count += 1
                    cloud_platform_delegated_domains.append(record_set.name)
                    found_delegation = True

                if not found_delegation:
                    unknown_delegations_count += 1
                    unkown_delegated_domains.append(record_set.name)

    logging.info(
        json.dumps(
            {
                "totals": {
                    "all": total_delegations,
                    "unknownDelegations": unknown_delegations_count,
                    "internalDelegations": internal_delgations_count,
                    "cloudPlatformDelegations": cloud_platform_delegations_count,
                },
                "delegations": {
                    "all": delegated_domains,
                    "cloudPlatform": cloud_platform_delegated_domains,
                    "internal": internal_delegated_domains,
                    "unkown": unkown_delegated_domains,
                },
            }
        )
    )


if __name__ == "__main__":
    main()
