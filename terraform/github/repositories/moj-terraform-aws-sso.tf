module "moj-terraform-aws-sso" {
  source = "github.com/ministryofjustice/operations-engineering-terraform-github-repositories?ref=0.0.1"

  type             = "module"
  name             = "moj-terraform-aws-sso"
  application_name = "moj-terraform-aws-sso"
  description      = "A Terraform module for setting up AWS SSO and Auth0, to allow users to sign-in to AWS using GitHub"
  topics           = ["aws", "terraform", "iam", "sso", "terraform-module", "civil-service", "aws-sso", "operations-engineering"]
  tags = {
    Team  = "operations-engineering"
    Phase = "production"
  }
}