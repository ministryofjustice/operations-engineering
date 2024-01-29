module "operations-engineering-certificate-renewal" {
  source  = "ministryofjustice/repository/github"
  version = "0.0.4"

  name             = "operations-engineering-certificate-renewal"
  application_name = "operations-engineering-certificate-renewal"
  description      = "An application to automatically manage the renewal of certificates, and notify when certificates are close to expiring."
}