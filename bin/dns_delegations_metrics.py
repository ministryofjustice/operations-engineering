from services.route53_service import Route53Service, HostedZoneModel
import json


def main():
    dsd_route53_service = Route53Service(profile="dsd_route53_read")
    cloud_platform_route53_service = Route53Service(
        profile="cloud_platform_route53_read"
    )

    dsd_hosted_zones: list[HostedZoneModel] = dsd_route53_service.get_hosted_zones()
    cloud_platform_hosted_zones: list[HostedZoneModel] = (
        cloud_platform_route53_service.get_hosted_zones()
    )

    print(json.dumps(dsd_hosted_zones[0].__dict__, default=lambda o: o.__dict__))
    print(
        json.dumps(
            cloud_platform_hosted_zones[0].__dict__, default=lambda o: o.__dict__
        )
    )


if __name__ == "__main__":
    main()
