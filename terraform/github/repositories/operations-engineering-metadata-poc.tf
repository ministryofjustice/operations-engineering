module "operations-engineering-metadata-poc" {
  source = "github.com/ministryofjustice/operations-engineering-terraform-github-repositories?ref=0.0.2"

  name             = "operations-engineering-metadata-poc"
  application_name = "operations-engineering-metadata-poc"
  description      = "PoC For Cross Identification Between MoJ Services"
  has_discussions = true
  tags = {
    Team  = "operations-engineering"
    Phase = "poc"
  }
  secrets = {
    DEVELOPMENT_ECR_ROLE_TO_ASSUME = ""
    DEV_KUBE_CERT = ""
    DEV_KUBE_NAMESPACE = ""
    DEV_KUBE_TOKEN = ""
    DEV_KUBE_CLUSTER = ""
  }
}