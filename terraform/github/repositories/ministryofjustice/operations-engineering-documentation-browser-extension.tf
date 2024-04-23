module "operations-engineering-documentation-browser-extension" {
  source  = "ministryofjustice/repository/github"
  version = "0.0.7"

  name        = "operations-engineering-documentation-browser-extension"
  description = "A browser extension to easily find documentation for building MoJ Digital Services"
  topics      = ["operations-engineering"]

  team_access = {
    admin = [var.operations_engineering_team_id]
  }
}