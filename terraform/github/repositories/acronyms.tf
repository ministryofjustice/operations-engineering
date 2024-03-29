module "acronyms" {
  source  = "ministryofjustice/repository/github"
  version = "0.0.7"

  name         = "acronyms"
  description  = "List of abbreviations used within the MoJ, and their definitions"
  homepage_url = "https://ministry-of-justice-acronyms.service.justice.gov.uk/"
  topics       = ["operations-engineering"]

  team_access = {
    admin = [data.github_team.operations_engineering.id]
  }
}