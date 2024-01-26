module "tech-docs-monitor" {
  source = "github.com/ministryofjustice/operations-engineering-terraform-github-repository?ref=0.0.2"

  name             = "tech-docs-monitor"
  application_name = "tech-docs-monitor"
  description      = "Part of alphagov/tech-docs-template (issues 👉https://github.com/alphagov/tech-docs-template/issues)"
  tags = {
    Team  = "operations-engineering"
    Phase = "production"
  }
}