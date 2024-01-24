module "terraform-aws-mtasts" {
  source = "github.com/ministryofjustice/operations-engineering-terraform-github-repositories?ref=0.0.2"

  name             = "terraform-aws-mtasts"
  application_name = "terraform-aws-mtasts"
  type             = "module"
  description      = "MTA-STS/TLS-RPT AWS Terraform Module"
  tags = {
    Team  = "operations-engineering"
    Phase = "production"
  }
}