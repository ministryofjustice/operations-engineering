module "moj-terraform-aws-sso" {
  source  = "ministryofjustice/repository/github"
  version = "0.0.4"

  type             = "module"
  name             = "moj-terraform-aws-sso"
  application_name = "moj-terraform-aws-sso"
  description      = "A Terraform module for setting up AWS SSO and Auth0, to allow users to sign-in to AWS using GitHub"
  topics           = ["aws", "terraform", "iam", "sso", "terraform-module", "civil-service", "aws-sso"]
}