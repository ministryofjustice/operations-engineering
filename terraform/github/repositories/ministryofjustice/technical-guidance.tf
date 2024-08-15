module "technical-guidance" {
  source  = "ministryofjustice/repository/github"
  version = "1.1.2"

  name         = "technical-guidance"
  description  = "How we build and operate products at the Ministry of Justice."
  homepage_url = "https://technical-guidance.service.justice.gov.uk/"
  topics       = ["operations-engineering"]

  team_access = {
    admin = [var.operations_engineering_team_id]
  }
}
