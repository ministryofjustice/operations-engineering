module "operations-engineering-reports" {
  source = "github.com/ministryofjustice/operations-engineering-terraform-github-repositories?ref=0.0.2"

  name             = "operations-engineering-reports"
  application_name = "operations-engineering-reports"
  description      = "Web application to receive JSON data and display data in reports using HTML."
  homepage_url     = "https://operations-engineering-reports.cloud-platform.service.justice.gov.uk/"
  topics           = ["flask", "reporting"]
  tags = {
    Team  = "operations-engineering"
    Phase = "production"
  }
  secrets = {
    AUTH0_CLIENT_ID                             = ""
    AUTH0_CLIENT_SECRET                         = ""
    DEVELOPMENT_ECR_ROLE_TO_ASSUME              = ""
    DEV_FLASK_APP_SECRET                        = ""
    FLASK_APP_SECRET                            = ""
    KUBE_CERT                                   = ""
    KUBE_CLUSTER                                = ""
    KUBE_NAMESPACE                              = ""
    KUBE_TOKEN                                  = ""
    PRODUCTION_ECR_ROLE_TO_ASSUME               = ""
    PROD_FLASK_APP_SECRET                       = ""
    SLACK_WEBHOOK_URL                           = ""
    CVE_SCAN_SLACK_WEBHOOK                      = ""
    DEV_OPERATIONS_ENGINEERING_REPORTS_API_KEY  = ""
    DEV_OPS_ENG_REPORTS_ENCRYPT_KEY             = ""
    OPERATIONS_ENGINEERING_REPORTS_API_KEY      = ""
    OPS_ENG_REPORTS_ENCRYPT_KEY                 = ""
    PROD_OPERATIONS_ENGINEERING_REPORTS_API_KEY = ""
    PROD_OPS_ENG_REPORTS_ENCRYPT_KEY            = ""
    ECR_REGISTRY                                = ""
  }
}