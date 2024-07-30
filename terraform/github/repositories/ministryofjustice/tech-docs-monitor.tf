module "tech-docs-monitor" {
  source  = "ministryofjustice/repository/github"
  version = "1.0.1"

  name        = "tech-docs-monitor"
  description = "Part of alphagov/tech-docs-template (issues 👉https://github.com/alphagov/tech-docs-template/issues)"
  topics      = ["operations-engineering"]

  team_access = {
    admin = [data.github_team.operations_engineering.id]
  }
}
