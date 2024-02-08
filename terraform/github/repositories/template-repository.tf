module "template-repository" {
  source  = "ministryofjustice/repository/github"
  version = "0.0.6"

  name        = "template-repository"
  type        = "template"
  description = "Github \"template\" repository, from which to create new MoJ Repositories with organisation defaults"
  topics      = ["operations-engineering"]
}