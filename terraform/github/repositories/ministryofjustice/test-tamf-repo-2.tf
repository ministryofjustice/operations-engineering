module "test_tamf_repo_2" {
  source  = "ministryofjustice/repository/github"
  version = "1.2.0"

  name        = "test-tamf-repo-2"
  description = "Test repo to test new module input team_access"
  topics      = ["operations-engineering"]
  team_access = {
    maintain = [var.operations_engineering_team_id]
  }
  secrets = { EXAMPLE_SECRET = jsondecode(data.aws_secretsmanager_secret_version.example_secret_version.secret_string)["EXAMPLE_SECRET"] }
}

data "aws_secretsmanager_secret" "example_secret" {
  name = "EXAMPLE_SECRET"
}

data "aws_secretsmanager_secret_version" "example_secret_version" {
  secret_id = data.aws_secretsmanager_secret.example_secret.id
}
