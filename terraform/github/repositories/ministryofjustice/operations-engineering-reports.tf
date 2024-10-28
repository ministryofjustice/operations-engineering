module "operations-engineering-reports" {
  source  = "ministryofjustice/repository/github"
  version = "1.2.1"

  poc = false

  name         = "operations-engineering-reports"
  description  = "Web application to receive JSON data and display data in reports using HTML."
  homepage_url = "https://operations-engineering-reports.cloud-platform.service.justice.gov.uk/"
  topics       = ["operations-engineering", "flask", "reporting"]

  team_access = {
    admin = [var.operations_engineering_team_id]
  }
  variables = {
    DEVELOPMENT_ECR_REGION     = var.ECR_REGION
    DEVELOPMENT_ECR_REPOSITORY = "operations-engineering/operations-engineering-reports-dev-ecr"
    ECR_REGISTRY               = var.ECR_REGISTRY
    PRODUCTION_ECR_REGION      = var.ECR_REGION
    PRODUCTION_ECR_REPOSITORY  = "operations-engineering/operations-engineering-reports-prod-ecr"
  }
}
