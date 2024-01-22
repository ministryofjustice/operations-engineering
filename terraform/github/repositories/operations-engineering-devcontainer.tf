module "operations-engineering-devcontainer" {
  source = "git::https://github.com/ministryofjustice/operations-engineering-terraform-github-repositories?ref=v0.0.1"

  name             = "operations-engineering-devcontainer"
  application_name = "operations-engineering-devcontainer"
  description      = ""
  topics           = ["operations-engineering"]
  tags = {
    Team  = "operations-engineering"
    Phase = "POC"
  }
}