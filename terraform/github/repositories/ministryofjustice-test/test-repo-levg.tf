module "test-repo-levg" {
  source  = "ministryofjustice/repository/github"
  version = var.module_version

  name        = "test-repo-levg"
  description = "test repo"
  topics      = ["operations-engineering"]
}
