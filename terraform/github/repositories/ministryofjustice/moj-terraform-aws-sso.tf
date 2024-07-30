module "moj-terraform-aws-sso" {
  source  = "ministryofjustice/repository/github"
  version = "1.0.1"

  type        = "module"
  name        = "moj-terraform-aws-sso"
  description = "A Terraform module for setting up AWS SSO and Auth0, to allow users to sign-in to AWS using GitHub"
  topics      = ["operations-engineering", "aws", "terraform", "iam", "sso", "terraform-module", "civil-service", "aws-sso"]

  team_access = {
    admin = [data.github_team.operations_engineering.id]
  }
}
