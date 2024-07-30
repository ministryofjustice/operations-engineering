module "github-collaborators" {
  source  = "ministryofjustice/repository/github"
  version = "1.0.1"

  name            = "github-collaborators"
  description     = "Manage outside collaborators on our Github repositories"
  has_discussions = true
  topics          = ["operations-engineering"]

  team_access = {
    admin = [data.github_team.operations_engineering.id]
  }
}
