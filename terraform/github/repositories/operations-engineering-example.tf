module "operations-engineering-example" {
  source  = "ministryofjustice/repository/github"
  version = "0.0.3"

  name             = "operations-engineering-example"
  application_name = "operations-engineering-example"
  description      = "Example application to showcase how to deploy code"
  homepage_url     = "https://operations-engineering-example-dev.cloud-platform.service.justice.gov.uk/"
}