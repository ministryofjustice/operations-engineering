module "tech-docs-monitor" {
  source  = "ministryofjustice/repository/github"
  version = "0.0.3"

  name             = "tech-docs-monitor"
  application_name = "tech-docs-monitor"
  description      = "Part of alphagov/tech-docs-template (issues 👉https://github.com/alphagov/tech-docs-template/issues)"
}