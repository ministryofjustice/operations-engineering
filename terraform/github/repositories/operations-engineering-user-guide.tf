module "operations-engineering-user-guide" {
  source  = "ministryofjustice/repository/github"
  version = "0.0.7"

  name         = "operations-engineering-user-guide"
  description  = "User documentation for Operations Engineering"
  homepage_url = "https://user-guide.operations-engineering.service.justice.gov.uk/"
  topics       = ["operations-engineering", "documentation", "user-guides"]
}