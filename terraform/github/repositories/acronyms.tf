module "acronyms" {
  source = "github.com/ministryofjustice/operations-engineering-terraform-github-repositories?ref=0.0.2"

  name             = "acronyms"
  application_name = "acronyms"
  description      = "List of abbreviations used within the MoJ, and their definitions"
  homepage_url     = "https://ministry-of-justice-acronyms.service.justice.gov.uk/"
  tags = {
    Team  = "operations-engineering"
    Phase = "production"
  }
  secrets = {
    SLACK_WEBHOOK_URL = ""
  }
}