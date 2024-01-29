module "moj-terraform-scim-github" {
  source  = "ministryofjustice/repository/github"
  version = "0.0.4"

  name             = "moj-terraform-scim-github"
  application_name = "moj-terraform-scim-github"
  description      = "Lambda function for automatic SCIM provisioning based on GitHub relationships"
}