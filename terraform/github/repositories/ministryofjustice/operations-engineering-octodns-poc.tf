module "operations-engineering-octodns-poc" {
  source  = "ministryofjustice/repository/github"
  version = "1.0.1"

  name        = "operations-engineering-octodns-poc"
  description = "This repository will be used to prove the concept of managing DNS records using OctoDNS."
  topics      = ["operations-engineering", "dns", "spike"]

  team_access = {
    admin = [data.github_team.operations_engineering.id]
  }
}
