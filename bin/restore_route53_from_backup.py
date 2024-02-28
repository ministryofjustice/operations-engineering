from services.s3_service import S3Service
from services.route_53_service import Route53Service
import os 
import sys
import json

def restore_route53_from_backup(s3_service: S3Service, r53_service: Route53Service, hosted_zones):
    s3_service._download_file('hosted_zones.json', 'hosted_zones.json')

    f = open('hosted_zones.json')

    json_data = json.load(f)

    f.close()

    r53_service.bulk_restore_hosted_zones(json_data, hosted_zones)

    os.remove("hosted_zones.json")


def main():
    s3_service = S3Service("cloud-platform-50ad54b3b789d9fba7b301cce9d35f39", "")
    r53_service = Route53Service()
    hosted_zones = sys.argv[0].split(',')
    restore_route53_from_backup(s3_service, r53_service, hosted_zones)

if __name__ == "__main__":
    main()