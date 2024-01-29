module "terraform-github-repository" {
  source = "github.com/ministryofjustice/operations-engineering-terraform-github-repository?ref=0.0.2"

  name             = "terraform-github-repository"
  application_name = "terraform-github-repository"
  description      = "A Terraform module for GiHub repositories in the Ministry of Justice"
  has_discussions  = true
  topics           = ["github", "terraform", "terraform-module"]
  type             = "module"
}