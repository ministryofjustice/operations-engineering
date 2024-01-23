module "operations-engineering-join-github" {
  source = "github.com/ministryofjustice/operations-engineering-terraform-github-repositories?ref=0.0.2"

  name             = "operations-engineering-join-github"
  application_name = "operations-engineering-join-github"
  description      = "An application to augment the process of joining a Ministry of Justice GitHub Organisation"
  homepage_url     = "https://join-github-dev.cloud-platform.service.justice.gov.uk/"
  tags = {
    Team  = "operations-engineering"
    Phase = "production"
  }
  secrets = {
    DEV_KUBE_CERT           = ""
    DEV_KUBE_NAMESPACE      = ""
    DEV_KUBE_TOKEN          = ""
    PROD_KUBE_CERT          = ""
    PROD_KUBE_NAMESPACE     = ""
    PROD_KUBE_TOKEN         = ""
    AUTH0_CLIENT_ID         = ""
    AUTH0_CLIENT_SECRET     = ""
    DEV_ADMIN_GITHUB_TOKEN  = ""
    DEV_ECR_ROLE_TO_ASSUME  = ""
    DEV_FLASK_APP_SECRET    = ""
    FLASK_APP_SECRET        = ""
    KUBE_CLUSTER            = ""
    PROD_KUBE_CERT          = ""
    PROD_KUBE_NAMESPACE     = ""
    PROD_KUBE_TOKEN         = ""
    PROD_ADMIN_GITHUB_TOKEN = ""
    PROD_ECR_ROLE_TO_ASSUME = ""
    PROD_FLASK_APP_SECRET   = ""
  }
}