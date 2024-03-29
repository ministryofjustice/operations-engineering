module "operations-engineering-support-metadata" {
  source  = "ministryofjustice/repository/github"
  version = "0.0.7"

  name            = "operations-engineering-support-metadata"
  description     = "This repository contains the data and tools for reporting Oerations Engineering support requests."
  homepage_url    = "https://operations-engineering-upport-metadata.operations-engineering.service.justice.gov.uk/"
  has_discussions = true
  topics          = ["operations-engineering"]

  team_access = {
    admin = [data.github_team.operations_engineering.id]
  }
}
