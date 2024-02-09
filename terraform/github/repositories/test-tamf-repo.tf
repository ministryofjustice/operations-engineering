module "test_tamf_repo" {
  source = "github.com/ministryofjustice/terraform-github-repository.git?ref=output-repo-name"

  name        = "test-tamf-repo"
  description = "Test repo to test team association"
  topics      = ["operations-engineering"]
}

resource "github_team_repository" "test_tamf_repo" {
  team_id    = data.github_team.operations_engineering.id
  repository = module.test_tamf_repo.repository_name
  permission = "admin"
}
