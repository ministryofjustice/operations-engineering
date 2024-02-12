data "github_team" "operations_engineering" {
  slug = "operations-engineering"
}

data "github_team" "operations_engineering_test" {
  provider = github.ministryofjustice-test
  slug     = "operations-engineering-test"
}