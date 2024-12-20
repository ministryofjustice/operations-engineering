module "operations-engineering-dns-form" {
  source  = "ministryofjustice/repository/github"
  version = "1.2.1"

  poc = false

  name         = "operations-engineering-dns-form"
  description  = "A web form that captures the requirements for a DNS change"
  homepage_url = "https://dev.change-dns.service.justice.gov.uk/"
  topics       = ["operations-engineering"]

  team_access = {
    admin = [var.operations_engineering_team_id]
  }
}
