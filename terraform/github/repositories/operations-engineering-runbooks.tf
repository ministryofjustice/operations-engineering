module "operations-engineering-runbooks" {
  source = "github.com/ministryofjustice/operations-engineering-terraform-github-repositories?ref=0.0.2"

  name             = "operations-engineering-runbooks"
  application_name = "operations-engineering-runbooks"
  description      = "Runbook documentation for Operations Engineering"
  homepage_url     = "https://runbooks.operations-engineering.service.justice.gov.uk/"
  topics           = ["documentation"]
  tags = {
    Team  = "operations-engineering"
    Phase = "production"
  }
}