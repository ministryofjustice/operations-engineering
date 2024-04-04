from services.route_53_service import Route53Service
from services.s3_service import S3Service


def export_hosted_zones_to_json(route_53_service: Route53Service):
    data_to_backup = route_53_service.bulk_export_route53_records()

    with open('hosted_zones.json', "w", encoding="utf-8") as json_file:
        json_file.write(data_to_backup)


# Use CP profile
def send_r53_backup_to_s3(s3_service: S3Service):
    s3_service.save_r53_backup_file()


def main():
    route_53_service = Route53Service()
    s3_service = S3Service("cloud-platform-50ad54b3b789d9fba7b301cce9d35f39", "")

    export_hosted_zones_to_json(route_53_service)
    send_r53_backup_to_s3(s3_service)


if __name__ == "__main__":
    main()
