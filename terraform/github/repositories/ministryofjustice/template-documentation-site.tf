module "template-documentation-site" {
  source  = "ministryofjustice/repository/github"
  version = "1.1.1"

  name         = "template-documentation-site"
  type         = "template"
  description  = "Template repo. for a gov.uk tech-docs-template documentation site published via github pages"
  homepage_url = "https://ministryofjustice.github.io/template-documentation-site/"
  topics       = ["operations-engineering"]

  team_access = {
    admin = [var.operations_engineering_team_id]
  }
}
