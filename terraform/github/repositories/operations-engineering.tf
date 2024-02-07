module "operations-engineering" {
  source  = "ministryofjustice/repository/github"
  version = "0.0.4"

  name             = "operations-engineering"
  application_name = "operations-engineering"
  description      = "This repository is home to the Operations Engineering's tools and utilities for managing, monitoring, and optimising software development processes at the Ministry of Justice."
  homepage_url     = "https://user-guide.operations-engineering.service.justice.gov.uk/"
  has_discussions  = true
  topics           = ["python", "issue-tracker"]
}