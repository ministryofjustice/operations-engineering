from services.s3_service import S3Service

def import_route53_backup(s3_service: S3Service):
    s3_service._download_file('hosted_zones.json', 'hosted_zones.json')

def main():
    s3_service = S3Service("cloud-platform-50ad54b3b789d9fba7b301cce9d35f39", "")
    import_route53_backup(s3_service)

if __name__ == "__main__":
    main()