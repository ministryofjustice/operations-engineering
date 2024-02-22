from services.route_53_service import Route53Service
import json

def test(route_53_service: Route53Service):
    data_to_backup = route_53_service.bulk_export_route53_records()
    print(json.dumps(data_to_backup, indent=4))

def main():
    route_53_service = Route53Service()
    test(route_53_service)

if __name__ == "__main__":
    main()
