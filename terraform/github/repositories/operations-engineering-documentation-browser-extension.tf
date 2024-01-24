module "operations-engineering-documentation-browser-extension" {
  source = "github.com/ministryofjustice/operations-engineering-terraform-github-repositories?ref=0.0.2"

  name             = "operations-engineering-documentation-browser-extension"
  application_name = "operations-engineering-documentation-browser-extension"
  description      = "A browser extension to easily find documentation for building MoJ Digital Services"
  tags = {
    Team  = "operations-engineering"
    Phase = "production"
  }
}