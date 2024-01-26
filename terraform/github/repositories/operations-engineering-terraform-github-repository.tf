module "operations-engineering-terraform-github-repository" {
  source = "github.com/ministryofjustice/operations-engineering-terraform-github-repository?ref=0.0.2"

  name             = "operations-engineering-terraform-github-repository"
  application_name = "operations-engineering-terraform-github-repository"
  description      = "A Terraform module for GiHub repositories in the Ministry of Justice"
  has_discussions  = true
  topics           = ["github", "terraform", "terraform-module"]
  type             = "module"
  tags = {
    Team  = "operations-engineering"
    Phase = "production"
  }
}