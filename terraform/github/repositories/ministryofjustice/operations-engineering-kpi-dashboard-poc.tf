module "operations-engineering-kpi-dashboard-poc" {
  source  = "ministryofjustice/repository/github"
  version = "1.0.0"

  name        = "operations-engineering-kpi-dashboard-poc"
  description = "A POC for displaying KPI metrics of processes and services"
  topics      = ["operations-engineering"]

  team_access = {
    admin = [var.operations_engineering_team_id]
  }
}
