module "operations-engineering-unit-test-generator-poc" {
  source  = "ministryofjustice/repository/github"
  version = "1.2.1"

  name        = "operations-engineering-unit-test-generator-poc"
  description = "CLI tool to automatically generate Python unit tests (unittest framework). This project is in POC."
  topics      = ["operations-engineering"]
  poc         = true

  team_access = {
    admin = [var.operations_engineering_team_id]
  }
}
