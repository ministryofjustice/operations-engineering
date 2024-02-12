module "test_tamf_repo_2" {
  source = "github.com/ministryofjustice/terraform-github-repository.git?ref=add-team-option"

  name        = "test-tamf-repo-2"
  description = "Test repo to test new module input team_access"
  topics      = ["operations-engineering"]
  team_access = {
    maintain = [data.github_team.operations_engineering.id]
  }
}