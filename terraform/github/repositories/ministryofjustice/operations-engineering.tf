module "operations-engineering" {
  source  = "ministryofjustice/repository/github"
  version = "1.2.1"

  poc = false

  name            = "operations-engineering"
  description     = "This repository is home to the Operations Engineering's tools and utilities for managing, monitoring, and optimising software development processes at the Ministry of Justice."
  homepage_url    = "https://cloud-optimisation-and-accountability.justice.gov.uk/documentation/operations-engineering-legacy/operations-engineering-user-guide/user-guide-index.html"
  has_discussions = true
  topics          = ["operations-engineering", "python", "issue-tracker"]

  team_access = {
    admin = [var.operations_engineering_team_id]
  }
}
