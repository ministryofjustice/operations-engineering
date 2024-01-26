module "cloud-platform-maintenance-pages" {
  source = "github.com/ministryofjustice/operations-engineering-terraform-github-repository?ref=0.0.2"

  name             = "cloud-platform-maintenance-pages"
  application_name = "cloud-platform-maintenance-pages"
  description      = "Web application to serve gov.uk maintenance pages for multiple domains"
  tags = {
    Team  = "operations-engineering"
    Phase = "production"
  }
}