module "operations-engineering-join-github" {
  source  = "ministryofjustice/repository/github"
  version = "0.0.3"

  name             = "operations-engineering-join-github"
  application_name = "operations-engineering-join-github"
  description      = "An application to augment the process of joining a Ministry of Justice GitHub Organisation"
  homepage_url     = "https://join-github-dev.cloud-platform.service.justice.gov.uk/"
}