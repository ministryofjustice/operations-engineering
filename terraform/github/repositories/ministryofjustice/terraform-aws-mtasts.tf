module "terraform-aws-mtasts" {
  source  = "ministryofjustice/repository/github"
  version = "1.1.1"

  name        = "terraform-aws-mtasts"
  type        = "module"
  description = "MTA-STS/TLS-RPT AWS Terraform Module"
  topics      = ["operations-engineering"]

  team_access = {
    admin = [var.operations_engineering_team_id]
  }
}
