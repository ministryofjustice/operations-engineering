module "technical-guidance" {
  source  = "ministryofjustice/repository/github"
  version = "0.0.7"

  name         = "technical-guidance"
  description  = "How we build and operate products at the Ministry of Justice."
  homepage_url = "https://technical-guidance.service.justice.gov.uk/"
  topics       = ["operations-engineering"]

  team_access = {
    admin = [data.github_team.operations_engineering.id]
  }
}