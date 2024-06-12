module "operations-engineering-dns-issues" {
  source  = "ministryofjustice/repository/github"
  version = "1.0.0"

  name        = "operations-engineering-dns-issues"
  description = "DNS change request issues related tp the DMS request app (https://github.com/ministryofjustice/operations-engineering-dns-form), whilst it is in development."
  topics      = ["operations-engineering", "dns"]
  visibility  = "internal"

  team_access = {
    admin = [var.operations_engineering_team_id]
  }
}
