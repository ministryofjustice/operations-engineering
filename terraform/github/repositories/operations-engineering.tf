module "operations-engineering" {
  source = "github.com/ministryofjustice/operations-engineering-terraform-github-repositories?ref=0.0.2"

  name             = "operations-engineering"
  application_name = "operations-engineering"
  description      = <<EOT
  This repository is home to the Operations Engineering's tools and utilities for managing, 
  monitoring, and optimising software development processes at the Ministry of Justice.
  EOT
  homepage_url     = "https://user-guide.operations-engineering.service.justice.gov.uk/"
  has_discussions  = true
  topics           = ["python", "issue-tracker"]
  tags = {
    Team  = "operations-engineering"
    Phase = "production"
  }
  secrets = {
    ADMIN_GITHUB_TOKEN_ENTERPRISE_DATA                    = ""
    ADMIN_SEND_TO_SLACK                                   = ""
    AUTH0_CLIENT_ID                                       = ""
    AUTH0_CLIENT_SECRET                                   = ""
    AUTH0_DOMAIN                                          = ""
    AUTH0_OPERATIONS_ENGINEERING_DEV_DEFAULT_CLIENTID     = ""
    AUTH0_OPERATIONS_ENGINEERING_DEV_DEFAULT_CLIENTSECRET = ""
    AUTH0_OPERATIONS_ENGINEERING_DEV_DOMAIN               = ""
    AUTO_REVIEW_DATE                                      = ""
    AWS_ID                                                = ""
    AWS_ID_DORMANT_USERS                                  = ""
    CLOUD_PLATFORM_MOJ_GITHUB_TOKEN                       = ""
    CODECOV_TOKEN                                         = ""
    GH_BOT_AUDIT_LOG_PAT_TOKEN                            = ""
    GH_BOT_PAT_TOKEN                                      = ""
    KUBE_CERT                                             = ""
    KUBE_CLUSTER                                          = ""
    KUBE_NAMESPACE                                        = ""
    KUBE_TOKEN                                            = ""
    LOGGING_LEVEL                                         = ""
    METADATA_API_TOKEN                                    = ""
    METADATA_API_URL                                      = ""
    NOTIFY_PROD_API_KEY                                   = ""
    NOTIFY_TEST_API_KEY                                   = ""
    OPERATIONS_ENGINEERING                                = ""
    OPS_BOT_TOKEN                                         = ""
    REPORTS_API_KEY                                       = ""
    ROUTE53_HOSTEDZONE_ID_1                               = ""
    ROUTE53_HOSTEDZONE_ID_2                               = ""
    S3_BUCKET_NAME                                        = ""
    SENTRY_TOKEN                                          = ""
    SLACK_BOT_TOKEN                                       = ""
    SLACK_WEBHOOK_URL                                     = ""
    SONAR_TOKEN                                           = ""
    TERRAFORM_ADMIN_DEV_LEVG                              = ""
    TERRAFORM_AUTH0_S3_ROLE_ARN_DEV                       = ""
    TERRAFORM_GITHUB_REPOS_S3_ROLE_ARN_DEV                = ""
    TERRAFORM_GITHUB_REPOS_S3_ROLE_ARN_PROD               = ""
  }
}