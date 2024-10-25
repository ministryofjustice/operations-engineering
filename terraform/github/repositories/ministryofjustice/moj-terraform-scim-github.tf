module "moj-terraform-scim-github" {
  source  = "ministryofjustice/repository/github"
  version = "1.2.1"

  poc = false

  name        = "moj-terraform-scim-github"
  description = "Lambda function for automatic SCIM provisioning based on GitHub relationships"
  topics      = ["operations-engineering"]

  team_access = {
    admin = [var.operations_engineering_team_id]
  }
}
