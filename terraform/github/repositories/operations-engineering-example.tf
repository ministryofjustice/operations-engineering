module "operations-engineering-example" {
  source = "github.com/ministryofjustice/operations-engineering-terraform-github-repositories?ref=0.0.2"

  name             = "operations-engineering-example"
  application_name = "operations-engineering-example"
  description      = "Example application to showcase how to deploy code"
  homepage_url     = "https://operations-engineering-example-dev.cloud-platform.service.justice.gov.uk/"
  tags = {
    Team  = "operations-engineering"
    Phase = "production"
  }
  secrets = {
    DEVELOPMENT_ECR_ROLE_TO_ASSUME = ""
    PRODUCTION_ECR_ROLE_TO_ASSUME  = ""
  }
}