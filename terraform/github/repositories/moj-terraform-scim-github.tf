module "moj-terraform-scim-github" {
  source  = "ministryofjustice/repository/github"
  version = "0.0.7"

  name        = "moj-terraform-scim-github"
  description = "Lambda function for automatic SCIM provisioning based on GitHub relationships"
  topics      = ["operations-engineering"]

  team_access = {
    admin = [data.github_team.operations_engineering.id]
  }
}