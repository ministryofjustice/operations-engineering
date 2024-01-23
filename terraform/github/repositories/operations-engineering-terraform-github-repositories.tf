module "operations-engineering-terraform-github-repositories" {
  source = "github.com/ministryofjustice/operations-engineering-terraform-github-repositories?ref=0.0.2"

  name             = "operations-engineering-terraform-github-repositories"
  application_name = "operations-engineering-terraform-github-repositories"
  description      = "A Terraform module for GiHub repositories in the Ministry of Justice"
  has_discussions  = true
  topics           = ["github", "terraform", "terraform-module"]
  type             = "module"
  tags = {
    Team  = "operations-engineering"
    Phase = "production"
  }
}