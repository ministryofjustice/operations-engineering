module "terraform-github-repository" {
  source  = "ministryofjustice/repository/github"
  version = "1.0.1"

  name            = "terraform-github-repository"
  description     = "A Terraform module for GitHub repositories in the Ministry of Justice"
  has_discussions = true
  topics          = ["operations-engineering", "github", "terraform", "terraform-module"]
  type            = "module"

  team_access = {
    admin = [data.github_team.operations_engineering.id]
  }
}
