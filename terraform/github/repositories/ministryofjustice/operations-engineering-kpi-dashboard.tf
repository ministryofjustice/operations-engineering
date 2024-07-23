module "operations-engineering-kpi-dashboard" {
  source  = "ministryofjustice/repository/github"
  version = "1.0.1"

  name        = "operations-engineering-kpi-dashboard"
  description = "Display KPI metrics of processes and services"
  topics      = ["operations-engineering"]

  team_access = {
    admin = [var.operations_engineering_team_id]
  }
}

moved {
  from = module.operations-engineering-kpi-dashboard-poc.github_branch_protection.default
  to   = module.operations-engineering-kpi-dashboard.github_branch_protection.default
}

moved {
  from = module.operations-engineering-kpi-dashboard-poc.github_repository.default
  to   = module.operations-engineering-kpi-dashboard.github_repository.default
}

moved {
  from = module.operations-engineering-kpi-dashboard-poc.github_repository_tag_protection.default
  to   = module.operations-engineering-kpi-dashboard.github_repository_tag_protection.default
}

moved {
  from = module.operations-engineering-kpi-dashboard-poc.github_team_repository.admin["4192115"]
  to   = module.operations-engineering-kpi-dashboard.github_team_repository.admin["4192115"]
}
