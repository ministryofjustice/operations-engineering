module "operations-engineering-devcontainer" {
  source  = "ministryofjustice/repository/github"
  version = "1.1.1"

  name        = "operations-engineering-devcontainer"
  description = ""
  topics      = ["operations-engineering"]

  team_access = {
    admin = [var.operations_engineering_team_id]
  }
}
