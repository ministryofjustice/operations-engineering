data "github_team" "operations_engineering_test" {
  provider = github.ministryofjustice-test
  slug     = "operations-engineering-test"
}

data "github_team" "test_team_access" {
  provider = github.ministryofjustice-test
  slug     = "test-team-access"
}
