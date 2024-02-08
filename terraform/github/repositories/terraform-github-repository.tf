module "terraform-github-repository" {
  source  = "ministryofjustice/repository/github"
  version = "0.0.6"

  name             = "terraform-github-repository"
  description      = "A Terraform module for GiHub repositories in the Ministry of Justice"
  has_discussions  = true
  topics           = ["operations-engineering", "github", "terraform", "terraform-module"]
  type             = "module"
}