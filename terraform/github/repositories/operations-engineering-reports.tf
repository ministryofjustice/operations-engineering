module "operations-engineering-reports" {
  source = "github.com/ministryofjustice/operations-engineering-terraform-github-repositories?ref=0.0.2"

  name             = "operations-engineering-reports"
  application_name = "operations-engineering-reports"
  description      = "Web application to receive JSON data and display data in reports using HTML."
  homepage_url = "https://operations-engineering-reports.cloud-platform.service.justice.gov.uk/"
  topics = ["flask", "reporting"]
  tags = {
    Team  = "operations-engineering"
    Phase = "production"
  }
  secrets = {
    AUTH0_CLIENT_ID = ""
    AUTH0_CLIENT_SECRET = ""
    DEVELOPMENT_ECR_ROLE_TO_ASSUME = ""
    DEV_FLASK_APP_SECRET = ""
    DEV_KUBE_CERT = ""
    DEV_KUBE_CLUSTER = ""
    DEV_KUBE_NAMESPACE = ""
    DEV_KUBE_TOKEN = ""
    FLASK_APP_SECRET = ""
    KUBE_CERT = ""
    KUBE_CLUSTER = ""
    KUBE_NAMESPACE = ""
    KUBE_TOKEN = ""
    PRODUCTION_ECR_ROLE_TO_ASSUME = ""
    PROD_FLASK_APP_SECRET = ""
    PROD_KUBE_CERT = ""
    PROD_KUBE_CLUSTER = ""
    PROD_KUBE_NAMESPACE = ""
    PROD_KUBE_TOKEN = ""
    SLACK_WEBHOOK_URL = ""
    CVE_SCAN_SLACK_WEBHOOK = ""
    DEV_OPERATIONS_ENGINEERING_REPORTS_API_KEY = ""
    DEV_OPS_ENG_REPORTS_ENCRYPT_KEY = ""
    OPERATIONS_ENGINEERING_REPORTS_API_KEY = ""
    OPS_ENG_REPORTS_ENCRYPT_KEY = ""
    PROD_OPERATIONS_ENGINEERING_REPORTS_API_KEY = ""
    PROD_OPS_ENG_REPORTS_ENCRYPT_KEY = ""
    ECR_REGISTRY = ""
  }
}