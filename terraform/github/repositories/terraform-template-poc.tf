module "terraform-template-poc" {
  source = "github.com/ministryofjustice/operations-engineering-terraform-github-repositories?ref=0.0.2"

  name             = "terraform-template-poc"
  application_name = "terraform-template-poc"
  type             = "template"
  description      = "A Proof of Concept for a resilient and scalable Terraform template, suitable for team use"
  topics           = ["standards-compliant"]
  tags = {
    Team  = "operations-engineering"
    Phase = "poc"
  }
}