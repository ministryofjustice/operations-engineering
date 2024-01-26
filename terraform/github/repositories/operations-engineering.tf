module "operations-engineering" {
  source = "github.com/ministryofjustice/operations-engineering-terraform-github-repository?ref=0.0.2"

  name             = "operations-engineering"
  application_name = "operations-engineering"
  description      = "This repository is home to the Operations Engineering's tools and utilities for managing, monitoring, and optimising software development processes at the Ministry of Justice."
  homepage_url     = "https://user-guide.operations-engineering.service.justice.gov.uk/"
  has_discussions  = true
  topics           = ["python", "issue-tracker"]
  tags = {
    Team  = "operations-engineering"
    Phase = "production"
  }
}