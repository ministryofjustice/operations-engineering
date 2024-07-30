module "terraform-aws-mtasts" {
  source  = "ministryofjustice/repository/github"
  version = "1.0.1"

  name        = "terraform-aws-mtasts"
  type        = "module"
  description = "MTA-STS/TLS-RPT AWS Terraform Module"
  topics      = ["operations-engineering"]

  team_access = {
    admin = [data.github_team.operations_engineering.id]
  }
}
