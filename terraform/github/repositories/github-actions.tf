module "github-actions" {
  source  = "ministryofjustice/repository/github"
  version = "0.0.6"

  name             = "github-actions"
  description      = "A github action which will run code formatters against PRs, and commit any resulting changes"
  topics           = ["operations-engineering"]
}