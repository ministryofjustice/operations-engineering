module "teraform-aws-route53-backup" {
  source  = "ministryofjustice/repository/github"
  version = "0.0.8"

  name              = "teraform-aws-route53-backup"
  description       = "A Terraform module for baclkup and restore of Amazon Route 53 records."
  has_discussions   = true
  topics            = ["operations-engineering", "terraform", "terraform-module"]
  type              = "module"
  visibilvisibility = "internal"

  team_access = {
    admin = [data.github_team.operations_engineering.id]
  }
}