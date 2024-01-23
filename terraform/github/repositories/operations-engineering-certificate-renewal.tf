module "operations-engineering-certificate-renewal" {
  source = "github.com/ministryofjustice/operations-engineering-terraform-github-repositories?ref=0.0.2"

  name             = "operations-engineering-certificate-renewal"
  application_name = "operations-engineering-certificate-renewal"
  description      = "An application to automatically manage the renewal of certificates, and notify when certificates are close to expiring."
  tags = {
    Team  = "operations-engineering"
    Phase = "production"
  }
  secrets = {
    AWS_ID = ""
    EXPIRE_TEMPLATE_ID = ""
    GANDI_API_KEY = ""
    GANDI_ORG_ID = ""
    NOTIFY_API_KEY = ""
    REPORT_TEMPLATE_ID = ""
    REQUEST_GANDI_FUNDS_REPORT_TEMPLATE_ID = ""
    REQUEST_GANDI_FUNDS_TEMPLATE_ID = ""
    S3_BUCKET_NAME = ""
    S3_OBJECT_NAME = ""
    SLACK_WEBHOOK_URL = ""
    SONAR_TOKEN = ""
    UNDELIVERED_REPORT_TEMPLATE_ID = ""
  }
}