module "operations-engineering-github-actions-dashboard" {
  source  = "ministryofjustice/repository/github"
  version = "1.0.1"

  name        = "operations-engineering-github-actions-dashboard"
  description = "A GitHub repository for the Operations Engineering GitHub Actions dashboard"
  topics      = ["operations-engineering"]

  team_access = {
    admin = [data.github_team.operations_engineering.id]
  }
}
