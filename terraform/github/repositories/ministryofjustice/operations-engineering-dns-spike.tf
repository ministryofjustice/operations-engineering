module "operations-engineering-dns-spike" {
  source  = "ministryofjustice/repository/github"
  version = "1.0.1"

  name        = "operations-engineering-dns-spike"
  description = "DNS spike for the operations engineering team"
  topics      = ["operations-engineering", "dns", "spike"]

  team_access = {
    admin = [data.github_team.operations_engineering.id]
  }
}
