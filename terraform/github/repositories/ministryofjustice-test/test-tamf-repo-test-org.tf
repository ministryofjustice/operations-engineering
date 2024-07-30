module "test_tamf_repo_test_org" {
  source  = "ministryofjustice/repository/github"
  version = "1.0.1"

  name        = "test-tamf-repo-test-org"
  description = "Test repo to test new module input team_access"
  topics      = ["operations-engineering"]
  team_access = {
    maintain = [data.github_team.operations_engineering_test.id]
    push     = [data.github_team.test_team_access.id]
  }
}
