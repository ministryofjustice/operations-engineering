module "operations-engineering-octodns-poc" {
  source  = "ministryofjustice/repository/github"
  version = "1.2.1"

  name        = "operations-engineering-octodns-poc"
  description = "This repository will be used to prove the concept of managing DNS records using OctoDNS."
  topics      = ["operations-engineering", "dns", "spike"]
  poc         = true

  team_access = {
    admin = [var.operations_engineering_team_id]
  }
}
