module "operations-engineering-devcontainer" {
  source = "github.com/ministryofjustice/operations-engineering-terraform-github-repositories?ref=0.0.1"

  name             = "operations-engineering-devcontainer"
  application_name = "operations-engineering-devcontainer"
  description      = ""
  tags = {
    Team  = "operations-engineering"
    Phase = "POC"
  }
}