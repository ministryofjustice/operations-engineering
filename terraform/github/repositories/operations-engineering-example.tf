module "operations-engineering-example" {
  source = "github.com/ministryofjustice/operations-engineering-terraform-github-repositories?ref=0.0.2"

  name             = "operations-engineering-example"
  application_name = "operations-engineering-example"
  description      = "Example application to showcase how to deploy code"
  homepage_url = "operations-engineering-example-dev.cloud-platform.service.justice.gov.uk/"
  tags = {
    Team  = "operations-engineering"
    Phase = "production"
  }
  secrets = {
    DEVELOPMENT_ECR_ROLE_TO_ASSUME = ""
    DEV_KUBE_CERT = ""
    DEV_KUBE_CLUSTER = ""
    DEV_KUBE_NAMESPACE = ""
    DEV_KUBE_TOKEN = ""
    PRODUCTION_ECR_ROLE_TO_ASSUME = ""
    PROD_KUBE_CERT = ""
    PROD_KUBE_CLUSTER = ""
    PROD_KUBE_NAMESPACE = ""
    PROD_KUBE_TOKEN = ""
  }
}