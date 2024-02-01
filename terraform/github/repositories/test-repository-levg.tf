module "test-repository-levg" {
  source  = "ministryofjustice/repository/github"
  version = "0.0.4"

  name             = "test-repository-levg"
  application_name = "test-repository-levg"
  description      = "test repo for demo"
  homepage_url     = "https://www.asda.com/"
}