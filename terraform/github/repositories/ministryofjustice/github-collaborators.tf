module "github-collaborators" {
  source  = "ministryofjustice/repository/github"
  version = "1.0.1"

  name            = "github-collaborators"
  description     = "Manage outside collaborators on our Github repositories lalalal"
  has_discussions = true
  topics          = ["operations-engineering"]

  team_access = {
    admin = [var.operations_engineering_team_id]
  }
}
