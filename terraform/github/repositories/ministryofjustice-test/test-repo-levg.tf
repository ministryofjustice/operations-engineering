module "test-repo-levg" {
  source   = "ministryofjustice/repository/github"
  version  = "0.0.4"
  provider = github.ministryofjustice-test

  name             = "test-repo-levg"
  application_name = "test-repo-levg"
  description      = "test repo"
}