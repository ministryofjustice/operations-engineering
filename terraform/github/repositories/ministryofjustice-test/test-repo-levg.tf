module "test-repo-levg" {
  source  = "ministryofjustice/repository/github"
  version = "1.0.1"

  name        = "test-repo-levg"
  description = "test repo"
  topics      = ["operations-engineering"]
}
