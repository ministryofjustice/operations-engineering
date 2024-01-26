module "template-documentation-site" {
  source = "github.com/ministryofjustice/operations-engineering-terraform-github-repository?ref=0.0.2"

  name             = "template-documentation-site"
  application_name = "template-documentation-site"
  type             = "template"
  description      = "Template repo. for a gov.uk tech-docs-template documentation site published via github pages"
  homepage_url     = "https://ministryofjustice.github.io/template-documentation-site/"
  tags = {
    Team  = "operations-engineering"
    Phase = "production"
  }
}