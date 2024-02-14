module "github-actions" {
  source  = "ministryofjustice/repository/github"
  version = "0.0.7"

  name        = "github-actions"
  description = "A github action which will run code formatters against PRs, and commit any resulting changes"
  topics      = ["operations-engineering"]

  team_access = {
    admin = [data.github_team.operations_engineering.id]
  }
}