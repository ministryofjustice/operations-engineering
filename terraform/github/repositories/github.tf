module "github" {
  source  = "ministryofjustice/repository/github"
  version = "0.0.7"

  name        = ".github"
  description = "Default organisational policies for the Ministry of Justice"
  topics      = ["operations-engineering"]

  team_access = {
    admin = [data.github_team.operations_engineering.id]
  }
}