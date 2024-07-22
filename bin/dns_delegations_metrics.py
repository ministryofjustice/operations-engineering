from services.route53_service import (
    RecordSetModel,
    RecordValueModel,
    Route53Service,
    HostedZoneModel,
)


def __is_delegated_to_hosted_zones(
    hosted_zones: list[HostedZoneModel], name_server_record: list[RecordValueModel]
):
    for hosted_zone in hosted_zones:
        hosted_zones_name_servers: RecordSetModel

        for record_set in hosted_zone.record_sets:
            if record_set.name == hosted_zone.name and record_set.type == "NS":
                hosted_zones_name_servers = record_set

        if (
            hosted_zones_name_servers
            and hosted_zones_name_servers == name_server_record
        ):
            return True
        else:
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
                if __is_delegated_to_hosted_zones(dsd_hosted_zones, record_set.values):
                    internal_delgations_count += 1
                    print(record_set.name, "delegated internally")

    print(internal_delgations_count)


if __name__ == "__main__":
    main()
