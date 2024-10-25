module "operations-engineering-example" {
  source  = "ministryofjustice/repository/github"
  version = "1.2.1"

  poc = false

  name         = "operations-engineering-example"
  description  = "Example application to showcase how to deploy code"
  homepage_url = "https://operations-engineering-example-dev.cloud-platform.service.justice.gov.uk/"
  topics       = ["operations-engineering"]

  team_access = {
    admin = [var.operations_engineering_team_id]
  }
  variables = {
    DEVELOPMENT_ECR_REGION     = var.ECR_REGION
    DEVELOPMENT_ECR_REPOSITORY = "operations-engineering/operations-engineering-example-dev"
    PRODUCTION_ECR_REGION      = var.ECR_REGION
    PRODUCTION_ECR_REPOSITORY  = "operations-engineering/operations-engineering-example-prod"
  }
}
