module "template-repository" {
  source = "github.com/ministryofjustice/operations-engineering-terraform-github-repository?ref=0.0.2"

  name             = "template-repository"
  application_name = "template-repository"
  type             = "template"
  description      = "Github \"template\" repository, from which to create new MoJ Repositories with organisation defaults"
  tags = {
    Team  = "operations-engineering"
    Phase = "production"
  }
}