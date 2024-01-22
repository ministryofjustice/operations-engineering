module "operations-engineering-devcontainer" {
  source = "github.com/ministryofjustice/operations-engineering-terraform-github-repositories"

  version = var.module_version

  name             = "operations-engineering-devcontainer"
  application_name = "operations-engineering-devcontainer"
  description      = ""
  topics           = ["operations-engineering"]
  tags = {
    Team  = "operations-engineering"
    Phase = "POC"
  }
}