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
