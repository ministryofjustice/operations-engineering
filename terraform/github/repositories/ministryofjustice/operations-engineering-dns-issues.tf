module "operations-engineering-dns-issues" {
  source  = "ministryofjustice/repository/github"
  version = "1.0.1"

  name        = "operations-engineering-dns-issues"
  description = "DNS requests are captured here as GitHub Issues. It should remain internal due to the sensitive nature of the information."
  topics      = ["operations-engineering", "dns"]
  visibility  = "internal"

  team_access = {
    admin = [data.github_team.operations_engineering.id]
  }
}
