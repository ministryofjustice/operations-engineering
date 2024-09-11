module "operations-engineering-cloud-platform-namespace" {
  source  = "ministryofjustice/repository/github"
  version = "1.1.2"

  name        = "operations-engineering-cloud-platform-namespace"
  description = "This repository contains the terraform code for an operations engineering namespace in the cloud platform"
  topics      = ["operations-engineering"]

  team_access = {
    admin = [var.operations_engineering_team_id]
  }
}
