module "operations-engineering-runbooks" {
  source  = "ministryofjustice/repository/github"
  version = "0.0.3"

  name             = "operations-engineering-runbooks"
  application_name = "operations-engineering-runbooks"
  description      = "Runbook documentation for Operations Engineering"
  homepage_url     = "https://runbooks.operations-engineering.service.justice.gov.uk/"
  topics           = ["documentation"]
}