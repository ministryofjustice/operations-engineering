module "operations-engineering-join-github" {
  source  = "ministryofjustice/repository/github"
  version = "1.1.1"

  name         = "operations-engineering-join-github"
  description  = "An application to augment the process of joining a Ministry of Justice GitHub Organisation"
  homepage_url = "https://dev.join-github.service.justice.gov.uk/"
  topics       = ["operations-engineering"]

  team_access = {
    admin = [var.operations_engineering_team_id]
  }
  variables = {
    DEV_ECR_REGION      = var.ECR_REGION
    DEV_ECR_REGISTRY    = var.ECR_REGISTRY
    DEV_ECR_REPOSITORY  = "operations-engineering/operations-engineering-join-github-dev"
    PROD_ECR_REGION     = var.ECR_REGION
    PROD_ECR_REGISTRY   = var.ECR_REGISTRY
    PROD_ECR_REPOSITORY = "operations-engineering/operations-engineering-join-github-prod"
  }
}
