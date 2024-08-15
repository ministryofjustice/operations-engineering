module "cloud-platform-maintenance-pages" {
  source  = "ministryofjustice/repository/github"
  version = "1.1.2"

  name        = "cloud-platform-maintenance-pages"
  description = "Web application to serve gov.uk maintenance pages for multiple domains"
  topics      = ["operations-engineering"]

  team_access = {
    admin = [var.operations_engineering_team_id]
  }
}
