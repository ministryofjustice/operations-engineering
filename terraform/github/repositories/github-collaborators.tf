module "github-collaborators" {
  source  = "ministryofjustice/repository/github"
  version = "0.0.3"

  name             = "github-collaborators"
  application_name = "github-collaborators"
  description      = "Manage outside collaborators on our Github repositories"
  has_discussions  = true
}