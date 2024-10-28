module "tech-docs-monitor" {
  source  = "ministryofjustice/repository/github"
  version = "1.2.1"

  poc = false

  name        = "tech-docs-monitor"
  description = "Part of alphagov/tech-docs-template (issues 👉https://github.com/alphagov/tech-docs-template/issues)"
  topics      = ["operations-engineering"]

  team_access = {
    admin = [var.operations_engineering_team_id]
  }
}
