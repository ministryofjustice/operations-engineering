module "github-actions" {
  source  = "ministryofjustice/repository/github"
  version = "1.1.1"

  name        = "github-actions"
  description = "A github action which will run code formatters against PRs, and commit any resulting changes"
  topics      = ["operations-engineering"]

  team_access = {
    admin = [var.operations_engineering_team_id]
  }
}
