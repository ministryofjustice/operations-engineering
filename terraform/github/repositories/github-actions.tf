module "github-actions" {
  source = "github.com/ministryofjustice/operations-engineering-terraform-github-repositories?ref=0.0.1"

  name             = "github-actions"
  application_name = "github-actions"
  description      = "A github action which will run code formatters against PRs, and commit any resulting changes"
  tags = {
    Team  = "operations-engineering"
    Phase = "production"
  }
}