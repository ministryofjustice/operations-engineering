module "cloud-platform-maintenance-pages" {
  source = "github.com/ministryofjustice/operations-engineering-terraform-github-repositories?ref=0.0.1"

  name             = "cloud-platform-maintenance-pages"
  application_name = "cloud-platform-maintenance-pages"
  description      = "Web application to serve gov.uk maintenance pages for multiple domains"
  tags = {
    Team  = "operations-engineering"
    Phase = "production"
  }
  secrets = {
    ECR_ROLE_TO_ASSUME = ""
    KUBE_CERT          = ""
    KUBE_CLUSTER       = ""
    KUBE_NAMESPACE     = ""
    KUBE_TOKEN         = ""
  }
}