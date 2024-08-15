module "test_tamf_repo_test_org" {
  source  = "ministryofjustice/repository/github"
  version = "1.1.2"

  name        = "test-tamf-repo-test-org"
  description = "Test repo to test new module input team_access"
  topics      = ["operations-engineering"]
  team_access = {
    maintain = [var.operations_engineering_test_team_id]
    push     = [var.test_team_access_team_id]
  }
}
