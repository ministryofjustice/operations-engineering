module "operations-engineering-certificate-renewal" {
  source  = "ministryofjustice/repository/github"
  version = "1.0.1"

  name        = "operations-engineering-certificate-renewal"
  description = "An application to automatically manage the renewal of certificates, and notify when certificates are close to expiring."
  topics      = ["operations-engineering"]

  team_access = {
    admin = [data.github_team.operations_engineering.id]
  }
}
