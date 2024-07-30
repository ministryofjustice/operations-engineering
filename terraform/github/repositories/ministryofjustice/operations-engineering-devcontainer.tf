module "operations-engineering-devcontainer" {
  source  = "ministryofjustice/repository/github"
  version = "1.0.1"

  name        = "operations-engineering-devcontainer"
  description = ""
  topics      = ["operations-engineering"]

  team_access = {
    admin = [data.github_team.operations_engineering.id]
  }
}
