module "operations-engineering-github-cloudwatch-alarms" {
  source  = "ministryofjustice/repository/github"
  version = "1.2.1"

  poc = false

  name        = "operations-engineering-github-cloudwatch-alarms"
  description = "IaC repository for CloudWatch alarms based on GitHub audit log data."
  topics      = ["operations-engineering"]

  team_access = {
    admin = [var.operations_engineering_team_id]
  }
}
