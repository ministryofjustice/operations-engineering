from services.route_53_service import Route53Service
import json

def export_hosted_zones_to_json(route_53_service: Route53Service):
    data_to_backup = route_53_service.bulk_export_route53_records()

    with open('hosted_zones.json', "w") as json_file:
        json_file.write(data_to_backup)

def main():
    route_53_service = Route53Service()
    export_hosted_zones_to_json(route_53_service)

if __name__ == "__main__":
    main()
