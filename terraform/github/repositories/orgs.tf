module "ministryofjustice" {
  source                              = "./ministryofjustice"
  ECR_REGION                          = var.ECR_REGION
  ECR_REGISTRY                        = var.ECR_REGISTRY
  operations_engineering_team_id      = data.github_team.operations_engineering.id
  operations_engineering_test_team_id = data.github_team.operations_engineering_test.id
  test_team_access_team_id            = data.github_team.test_team_access.id
}

module "ministryofjustice-test" {
  source = "./ministryofjustice-test"
  providers = {
    github = github.ministryofjustice-test
  }
}