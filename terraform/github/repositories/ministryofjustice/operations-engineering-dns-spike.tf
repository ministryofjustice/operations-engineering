module "operations-engineering-dns-spike" {
  source  = "ministryofjustice/repository/github"
  version = "1.2.1"

  poc = false

  name        = "operations-engineering-dns-spike"
  description = "DNS spike for the operations engineering team"
  topics      = ["operations-engineering", "dns", "spike"]

  team_access = {
    admin = [var.operations_engineering_team_id]
  }
}
