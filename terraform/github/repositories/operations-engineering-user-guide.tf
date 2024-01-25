module "operations-engineering-user-guide" {
  source = "github.com/ministryofjustice/operations-engineering-terraform-github-repositories?ref=0.0.2"

  name             = "operations-engineering-user-guide"
  application_name = "operations-engineering-user-guide"
  description      = "User documentation for Operations Engineering"
  homepage_url     = "https://user-guide.operations-engineering.service.justice.gov.uk/"
  topics           = ["documentation", "user-guides"]
  tags = {
    Team  = "operations-engineering"
    Phase = "production"
  }
}