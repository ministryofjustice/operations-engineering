module "github-collaborators" {
  source  = "ministryofjustice/repository/github"
  version = "0.0.6"

  name             = "github-collaborators"
  description      = "Manage outside collaborators on our Github repositories"
  has_discussions  = true
  topics           = ["operations-engineering"]
}