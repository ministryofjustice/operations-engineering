module "operations-engineering-kpi-dashboard" {
  source  = "ministryofjustice/repository/github"
  version = "1.1.2"

  name        = "operations-engineering-kpi-dashboard"
  description = "Display KPI metrics of processes and services"
  topics      = ["operations-engineering"]

  team_access = {
    admin = [var.operations_engineering_team_id]
  }
}
