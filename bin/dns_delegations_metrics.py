import logging

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
        print(f"Checking if Delegated to HostedZone: [ {hosted_zone.name} ]")

        if hosted_zone.name != name_server_record.name:
            # print("Not Delegated Because HostedZone Name Does Not Match Record Name")
            continue

        hosted_zones_name_servers: RecordSetModel | bool = False

        for record_set in hosted_zone.record_sets:
            if record_set.name == hosted_zone.name and record_set.type == "NS":
                hosted_zones_name_servers = record_set

        if not hosted_zones_name_servers:
            logging.warn(f"HostedZone [ ${hosted_zone.name} ] does not have NS record")
            continue

        name_servers_to_check = __flatten_record_value(name_server_record.values)
        hosted_zone_name_servers = __flatten_record_value(
            hosted_zones_name_servers and hosted_zones_name_servers.values
        )

        if hosted_zone.name == "et.dsd.io.":
            print(f"HostedZone NameServers Flat: [ ${hosted_zone_name_servers} ]")
            print(f"Delegation NameServers Flat: [ ${name_servers_to_check} ]")

        if name_servers_to_check == hosted_zone_name_servers:
            print("Found Delegation!")
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

    for hosted_zone in dsd_hosted_zones:
        print("Checking HostedZone:", hosted_zone.name)
        for record_set in hosted_zone.record_sets:
            print("Checking RecordSet:", record_set.name)
            is_delegation = (
                True
                if record_set.type == "NS" and record_set.name != hosted_zone.name
                else False
            )
            if is_delegation:
                print("Checking Delegation: ", record_set)
                if __is_delegated_to_hosted_zones(dsd_hosted_zones, record_set):
                    internal_delgations_count += 1
                    print(record_set.name, "delegated internally")

    print(internal_delgations_count)


if __name__ == "__main__":
    main()
