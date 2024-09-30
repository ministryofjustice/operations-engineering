module "operations-engineering-runbooks" {
  source  = "ministryofjustice/repository/github"
  version = "1.2.0"

  name         = "operations-engineering-runbooks"
  description  = "Runbook documentation for Operations Engineering"
  homepage_url = "https://runbooks.operations-engineering.service.justice.gov.uk/"
  topics       = ["operations-engineering", "documentation"]

  team_access = {
    admin = [var.operations_engineering_team_id]
  }
}
