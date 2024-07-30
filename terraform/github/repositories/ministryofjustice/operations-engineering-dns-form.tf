module "operations-engineering-dns-form" {
  source  = "ministryofjustice/repository/github"
  version = "1.0.1"

  name        = "operations-engineering-dns-form"
  description = "A web form that captures the requirements for a DNS change"
  topics      = ["operations-engineering"]

  team_access = {
    admin = [data.github_team.operations_engineering.id]
  }
}
