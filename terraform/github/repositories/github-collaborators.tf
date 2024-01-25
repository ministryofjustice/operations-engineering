module "github-collaborators" {
  source = "github.com/ministryofjustice/operations-engineering-terraform-github-repositories?ref=0.0.2"

  name             = "github-collaborators"
  application_name = "github-collaborators"
  description      = "Manage outside collaborators on our Github repositories"
  has_discussions  = true
  tags = {
    Team  = "operations-engineering"
    Phase = "production"
  }
}