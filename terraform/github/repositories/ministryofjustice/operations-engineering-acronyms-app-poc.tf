module "operations-engineering-acronyms-app-poc" {
  source  = "ministryofjustice/repository/github"
  version = "1.2.0"

  name        = "operations-engineering-acronyms-app-poc"
  description = "A web app for viewing and adding acronyms, featuring sentiment analysis validation."
  topics      = ["operations-engineering", "poc"]
  visibility  = "public"

  template = {
    owner      = "ministryofjustice"
    repository = "operations-engineering-flask-template"
  }

  team_access = {
    admin = [var.operations_engineering_team_id]
  }
}
