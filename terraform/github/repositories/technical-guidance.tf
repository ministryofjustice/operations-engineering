module "technical-guidance" {
  source  = "ministryofjustice/repository/github"
  version = "0.0.4"

  name             = "technical-guidance"
  application_name = "technical-guidance"
  description      = "How we build and operate products at the Ministry of Justice."
  homepage_url     = "https://technical-guidance.service.justice.gov.uk/"
}