# module "operations-engineering-kpi-dashboard" {
#   source  = "ministryofjustice/repository/github"
#   version = "1.2.1"

#   poc = false

#   name         = "operations-engineering-kpi-dashboard"
#   description  = "Display KPI metrics of processes and services"
#   homepage_url = "https://kpi-dashboard.cloud-platform.service.justice.gov.uk/dashboard"
#   topics       = ["operations-engineering"]

#   team_access = {
#     admin = [var.operations_engineering_team_id]
#   }
# }
