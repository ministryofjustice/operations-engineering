module "technical-guidance" {
  source = "github.com/ministryofjustice/operations-engineering-terraform-github-repositories?ref=0.0.2"

  name             = "technical-guidance"
  application_name = "technical-guidance"
  description      = "How we build and operate products at the Ministry of Justice."
  homepage_url     = "https://technical-guidance.service.justice.gov.uk/"
  tags = {
    Team  = "operations-engineering"
    Phase = "production"
  }
  secrets = {
    GH_BOT_PAT_TOKEN       = ""
    OPERATIONS_ENGINEERING = ""
    OPS_BOT_TOKEN          = ""
    SLACK_WEBHOOK_URL      = ""
  }
}