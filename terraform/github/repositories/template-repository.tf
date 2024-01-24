module "template-repository" {
  source = "github.com/ministryofjustice/operations-engineering-terraform-github-repositories?ref=0.0.2"

  name             = "template-repository"
  application_name = "template-repository"
  type             = "template"
  description      = "Github \"template\" repository, from which to create new MoJ Repositories with organisation defaults"
  homepage_url     = "https://hub.docker.com/r/ministryofjustice/tech-docs-github-pages-publisher"
  tags = {
    Team  = "operations-engineering"
    Phase = "production"
  }
}