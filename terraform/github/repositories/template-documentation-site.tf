module "template-documentation-site" {
  source  = "ministryofjustice/repository/github"
  version = "0.0.4"

  name             = "template-documentation-site"
  application_name = "template-documentation-site"
  type             = "template"
  description      = "Template repo. for a gov.uk tech-docs-template documentation site published via github pages"
  homepage_url     = "https://ministryofjustice.github.io/template-documentation-site/"
}