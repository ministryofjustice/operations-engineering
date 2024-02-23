from services.s3_service import S3Service

def send_r53_backup_to_s3(s3_service: S3Service):
    s3_service.save_r53_backup_file()

def main():
    s3_service = S3Service("cloud-platform-50ad54b3b789d9fba7b301cce9d35f39")
    send_r53_backup_to_s3(s3_service)

if __name__ == "__main__":
    main()