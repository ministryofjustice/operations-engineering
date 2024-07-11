module "operations-engineering-test-secrets-manager" {
  source  = "ministryofjustice/repository/github"
  version = "1.0.1"

  name        = "operations-engineering-test-secrets-manager"
  description = "A test repository for the secret manager PoC."
  topics      = ["operations-engineering"]

  team_access = {
    admin = [var.operations_engineering_team_id]
  }
}

data "aws_secretsmanager_secret" "example_secret" {
  name = "EXAMPLE_SECRET"
}

data "aws_secretsmanager_secret_version" "example_secret_version" {
  secret_id = data.aws_secretsmanager_secret.example_secret.id
}

resource "github_actions_secret" "example_secret" {
  repository      = "operations-engineering-test-secrets-manager"
  secret_name     = "EXAMPLE_SECRET"
  plaintext_value = jsondecode(data.aws_secretsmanager_secret_version.example.secret_string)["EXAMPLE_SECRET"]
}
