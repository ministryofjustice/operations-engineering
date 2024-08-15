module "template-repository" {
  source  = "ministryofjustice/repository/github"
  version = "1.1.2"

  name        = "template-repository"
  type        = "template"
  description = "Github \"template\" repository, from which to create new MoJ Repositories with organisation defaults"
  topics      = ["operations-engineering"]

  team_access = {
    admin = [var.operations_engineering_team_id]
  }
}
