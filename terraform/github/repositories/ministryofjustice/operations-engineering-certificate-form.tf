module "operations-engineering-certificate-form" {
  source  = "ministryofjustice/repository/github"
  version = "1.2.1"

  poc = true

  name        = "operations-engineering-certificate-form"
  description = "An experimental web form that assists with automating part of the certificate renewal process."
  topics      = ["operations-engineering"]

  template = {
    owner      = "ministryofjustice"
    repository = "operations-engineering-flask-template"
  }

  team_access = {
    admin = [var.operations_engineering_team_id]
  }
}
