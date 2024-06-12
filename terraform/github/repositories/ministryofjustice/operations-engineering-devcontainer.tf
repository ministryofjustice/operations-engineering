module "operations-engineering-devcontainer" {
  source  = "ministryofjustice/repository/github"
  version = var.module_version

  name        = "operations-engineering-devcontainer"
  description = ""
  topics      = ["operations-engineering"]

  team_access = {
    admin = [var.operations_engineering_team_id]
  }
}
