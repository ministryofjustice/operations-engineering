from services.route53_service import Route53Service


def main():
    dsd_route53_service = Route53Service(profile="dsd_route53_read")
    cloud_platform_route53_service = Route53Service(
        profile="cloud_platform_route53_read"
    )

    print(dsd_route53_service.get_route53_hosted_zones()[0].name)
    print(cloud_platform_route53_service.get_route53_hosted_zones()[0].name)


if __name__ == "__main__":
    main()
