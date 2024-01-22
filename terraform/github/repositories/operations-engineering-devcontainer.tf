module "operations-engineering-devcontainer" {
  source = "https://github.com/ministryofjustice/operations-engineering-terraform-github-repositories/releases/tag/0.0.1"

  name             = "operations-engineering-devcontainer"
  application_name = "operations-engineering-devcontainer"
  description      = ""
  topics           = ["operations-engineering"]
  tags = {
    Team  = "operations-engineering"
    Phase = "POC"
  }
}