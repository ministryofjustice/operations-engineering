module "operations-engineering-documentation-browser-extension" {
  source  = "ministryofjustice/repository/github"
  version = "0.0.4"

  name             = "operations-engineering-documentation-browser-extension"
  application_name = "operations-engineering-documentation-browser-extension"
  description      = "A browser extension to easily find documentation for building MoJ Digital Services"
}