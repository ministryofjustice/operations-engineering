module "tech-docs-monitor" {
  source  = "ministryofjustice/repository/github"
  version = "0.0.7"

  name        = "tech-docs-monitor"
  description = "Part of alphagov/tech-docs-template (issues 👉https://github.com/alphagov/tech-docs-template/issues)"
  topics      = ["operations-engineering"]
}