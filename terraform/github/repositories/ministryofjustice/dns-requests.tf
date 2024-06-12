module "dns_requests" {
  source  = "ministryofjustice/repository/github"
  version = "0.0.7"

  name        = "DNS Change Requests"
  description = "DNS change request issues related tp the DMS request app (https://github.com/ministryofjustice/operations-engineering-dns-form), whilst it is in development."
  topics      = ["operations-engineering", "dns"]
  visibility  = "internal"

  team_access = {
    admin = [var.operations_engineering_team_id]
  }
}
