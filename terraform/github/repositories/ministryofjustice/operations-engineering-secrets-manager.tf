module "operations-engineering-secrets-manager" {
  source  = "ministryofjustice/repository/github"
  version = "1.0.1"

  name        = "operations-engineering-secrets-manager"
  description = "A GitHub repository to synchronise secrets between AWS Secrets Manager and Operations Engineering repositories."
  topics      = ["operations-engineering", "terraform"]

  team_access = {
    admin = [var.operations_engineering_team_id]
  }
}
