module "operations-engineering-certificate-renewal" {
  source  = "ministryofjustice/repository/github"
  version = "0.0.6"

  name        = "operations-engineering-certificate-renewal"
  description = "An application to automatically manage the renewal of certificates, and notify when certificates are close to expiring."
  topics      = ["operations-engineering"]
}