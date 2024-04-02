module "test_tamf_repo_2" {
  source  = "ministryofjustice/repository/github"
  version = "0.0.7"

  name        = "test-tamf-repo-2"
  description = "Test repo to test new module input team_access"
  topics      = ["operations-engineering"]
  team_access = {
    maintain = [var.operations_engineering_team_id]
  }
}