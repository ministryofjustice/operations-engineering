module "operations-engineering-dns-form" {
  source  = "ministryofjustice/repository/github"
  version = var.module_version

  name        = "operations-engineering-dns-form"
  description = "A web form that captures the requirements for a DNS change"
  topics      = ["operations-engineering"]

  team_access = {
    admin = [var.operations_engineering_team_id]
  }
}
