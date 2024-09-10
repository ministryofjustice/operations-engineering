module "operations-engineering-flask-template" {
  source  = "ministryofjustice/repository/github"
  version = "1.1.2"

  name        = "operations-engineering-flask-template"
  type        = "template"
  description = "Template repository containing a Flask application used by the Operations Engineering team."
  topics      = ["operations-engineering"]

  team_access = {
    admin = [var.operations_engineering_team_id]
  }
}
