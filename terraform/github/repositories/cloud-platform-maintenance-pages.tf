module "cloud-platform-maintenance-pages" {
  source  = "ministryofjustice/repository/github"
  version = "0.0.6"

  name             = "cloud-platform-maintenance-pages"
  description      = "Web application to serve gov.uk maintenance pages for multiple domains"
  topics           = ["operations-engineering"]  
}