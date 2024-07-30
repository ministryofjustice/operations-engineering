module "operations-engineering-example" {
  source  = "ministryofjustice/repository/github"
  version = "1.0.1"

  name         = "operations-engineering-example"
  description  = "Example application to showcase how to deploy code"
  homepage_url = "https://operations-engineering-example-dev.cloud-platform.service.justice.gov.uk/"
  topics       = ["operations-engineering"]

  team_access = {
    admin = [data.github_team.operations_engineering.id]
  }
  variables = {
    DEVELOPMENT_ECR_REGION     = var.ECR_REGION
    DEVELOPMENT_ECR_REPOSITORY = "operations-engineering/operations-engineering-example-dev"
    PRODUCTION_ECR_REGION      = var.ECR_REGION
    PRODUCTION_ECR_REPOSITORY  = "operations-engineering/operations-engineering-example-prod"
  }
}
