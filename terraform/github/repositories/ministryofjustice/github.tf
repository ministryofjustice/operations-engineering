module "github" {
  source  = "ministryofjustice/repository/github"
  version = "1.1.1"

  name        = ".github"
  description = "Default organisational policies for the Ministry of Justice"
  topics      = ["operations-engineering"]

  team_access = {
    admin = [var.operations_engineering_team_id]
  }
}
