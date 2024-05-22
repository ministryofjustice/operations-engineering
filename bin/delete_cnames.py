import sys
from services.route_53_service import Route53Service


def main():
    print("Start")

    if len(sys.argv) < 1:
        raise ValueError("Please specify hosted zones as CLI arguments")

    route53_service = Route53Service()

    hosted_zones = sys.argv

    for zone in hosted_zones:
        route53_service.delete_cname_records(zone)

    print("Finished")


if __name__ == "__main__":
    main()
