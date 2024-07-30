module "cloud-platform-maintenance-pages" {
  source  = "ministryofjustice/repository/github"
  version = "1.0.1"

  name        = "cloud-platform-maintenance-pages"
  description = "Web application to serve gov.uk maintenance pages for multiple domains"
  topics      = ["operations-engineering"]

  team_access = {
    admin = [data.github_team.operations_engineering.id]
  }
}
