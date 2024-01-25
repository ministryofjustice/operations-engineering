module "operations-engineering-certificate-renewal" {
  source = "github.com/ministryofjustice/operations-engineering-terraform-github-repositories?ref=0.0.2"

  name             = "operations-engineering-certificate-renewal"
  application_name = "operations-engineering-certificate-renewal"
  description      = "An application to automatically manage the renewal of certificates, and notify when certificates are close to expiring."
  tags = {
    Team  = "operations-engineering"
    Phase = "production"
  }
}