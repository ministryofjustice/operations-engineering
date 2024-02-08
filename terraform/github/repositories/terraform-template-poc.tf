module "terraform-template-poc" {
  source  = "ministryofjustice/repository/github"
  version = "0.0.6"

  name             = "terraform-template-poc"
  type             = "template"
  description      = "A Proof of Concept for a resilient and scalable Terraform template, suitable for team use"
  topics           = ["operations-engineering", "standards-compliant"]
}