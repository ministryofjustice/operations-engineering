module "acronyms" {
  source  = "ministryofjustice/repository/github"
  version = "0.0.6"

  name             = "acronyms"
  description      = "List of abbreviations used within the MoJ, and their definitions"
  homepage_url     = "https://ministry-of-justice-acronyms.service.justice.gov.uk/"
  topics           = ["operations-engineering"]
}