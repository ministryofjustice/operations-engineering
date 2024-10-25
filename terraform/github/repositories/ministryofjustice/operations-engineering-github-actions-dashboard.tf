module "operations-engineering-github-actions-dashboard" {
  source  = "ministryofjustice/repository/github"
  version = "1.2.1"

  poc = false

  name        = "operations-engineering-github-actions-dashboard"
  description = "A GitHub repository for the Operations Engineering GitHub Actions dashboard"
  topics      = ["operations-engineering"]

  team_access = {
    admin = [var.operations_engineering_team_id]
  }
}
