module "test-repo-levg" {
  source  = "ministryofjustice/repository/github"
  version = "1.2.1"

  poc = false

  name        = "test-repo-levg"
  description = "test repo"
  topics      = ["operations-engineering"]
}
