module "test-repo2-levg" {
  source  = "ministryofjustice/repository/github"
  version = "0.0.6"
  providers = {
    github = github.ministryofjustice-test
  }

  name        = "test-repo2-levg"
  description = "test repo2"
  topics      = ["operations-engineering"]
}