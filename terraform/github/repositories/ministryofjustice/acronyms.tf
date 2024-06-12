module "acronyms" {
  source  = "ministryofjustice/repository/github"
  version = var.module_version

  name         = "acronyms"
  description  = "List of abbreviations used within the MoJ, and their definitions"
  homepage_url = "https://ministry-of-justice-acronyms.service.justice.gov.uk/"
  topics       = ["operations-engineering"]

  team_access = {
    admin = [var.operations_engineering_team_id]
  }
}
