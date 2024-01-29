module "acronyms" {
  source  = "ministryofjustice/repository/github"
  version = "0.0.3"

  name             = "acronyms"
  application_name = "acronyms"
  description      = "List of abbreviations used within the MoJ, and their definitions"
  homepage_url     = "https://ministry-of-justice-acronyms.service.justice.gov.uk/"
}