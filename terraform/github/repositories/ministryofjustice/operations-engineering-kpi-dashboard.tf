module "operations-engineering-kpi-dashboard" {
  source  = "ministryofjustice/repository/github"
  version = "1.1.1"

  name        = "operations-engineering-kpi-dashboard"
  description = "Display KPI metrics of processes and services"
  topics      = ["operations-engineering"]

  team_access = {
    admin = [data.github_team.operations_engineering.id]
  }
}
