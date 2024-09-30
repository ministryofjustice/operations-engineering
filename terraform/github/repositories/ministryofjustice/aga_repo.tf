module "operations-engineering-aga-test" {
  source  = "ministryofjustice/repository/github"
  version = "1.2.0"

  name        = "operations-engineering-aga-test"
  description = "this is a test and will be deleted"
  topics      = ["operations-engineering", "poc"]
  visibility  = "public"

  template    = {
    owner      = "ministryofjustice"
    repository = "operations-engineering-flask-template"
  }

  team_access = {
    admin = [var.operations_engineering_team_id]
  }
}
