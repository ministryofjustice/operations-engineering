module "acronyms" {
  source  = "ministryofjustice/repository/github"
  version = "1.0.1"

  name        = "acronyms"
  description = "List of abbreviations used within the MoJ, and their definitions"
  topics      = ["operations-engineering"]

  team_access = {
    admin = [data.github_team.operations_engineering.id]
  }
}
