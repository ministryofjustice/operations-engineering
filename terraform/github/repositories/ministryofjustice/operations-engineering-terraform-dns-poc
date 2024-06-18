module "operations-engineering-terraform-dns-poc" {
  source  = "ministryofjustice/repository/github"
  version = "1.0.1"

  name        = "operations-engineering-terraform-dns-poc"
  description = "This repository will be used to prove the concept of managing DNS records using Terraform."
  topics      = ["operations-engineering", "dns", "spike"]

  team_access = {
    admin = [var.operations_engineering_team_id]
  }
}
