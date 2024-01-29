module "terraform-aws-mtasts" {
  source  = "ministryofjustice/repository/github"
  version = "0.0.3"

  name             = "terraform-aws-mtasts"
  application_name = "terraform-aws-mtasts"
  type             = "module"
  description      = "MTA-STS/TLS-RPT AWS Terraform Module"
}