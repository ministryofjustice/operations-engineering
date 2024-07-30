module "template-repository" {
  source  = "ministryofjustice/repository/github"
  version = "1.0.1"

  name        = "template-repository"
  type        = "template"
  description = "Github \"template\" repository, from which to create new MoJ Repositories with organisation defaults"
  topics      = ["operations-engineering"]

  team_access = {
    admin = [data.github_team.operations_engineering.id]
  }
}
