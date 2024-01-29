module "terraform-template-poc" {
  source  = "ministryofjustice/repository/github"
  version = "0.0.4"

  name             = "terraform-template-poc"
  application_name = "terraform-template-poc"
  type             = "template"
  description      = "A Proof of Concept for a resilient and scalable Terraform template, suitable for team use"
  topics           = ["standards-compliant"]
}