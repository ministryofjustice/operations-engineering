module "test-repo-levg" {
  source  = "ministryofjustice/repository/github"
  version = "1.2.0"

  name        = "test-repo-levg"
  description = "test repo"
  topics      = ["operations-engineering"]
}
