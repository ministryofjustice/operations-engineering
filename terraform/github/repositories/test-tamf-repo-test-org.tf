module "test_tamf_repo_test_org" {
  source = "github.com/ministryofjustice/terraform-github-repository.git?ref=add-team-option"

  providers = {
    github = github.ministryofjustice-test
  }

  name        = "test-tamf-repo-test-org"
  description = "Test repo to test new module input team_access"
  topics      = ["operations-engineering"]
  team_access = {
    maintain = [data.github_team.operations_engineering_test.id]
  }
}