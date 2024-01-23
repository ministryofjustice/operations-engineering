module "github-collaborators" {
  source = "github.com/ministryofjustice/operations-engineering-terraform-github-repositories"

  name             = "github-collaborators"
  application_name = "github-collaborators"
  description      = "Manage outside collaborators on our Github repositories"
  has_discussions  = true
  tags = {
    Team  = "operations-engineering"
    Phase = "production"
  }
  secrets = {
    APP_ID                = ""
    APP_INSTALLATION_ID   = ""
    APP_PEM_FILE          = ""
    AWS_ACCESS_KEY_ID     = ""
    AWS_SECRET_ACCESS_KEY = ""
    NOTIFY_PROD_TOKEN     = ""
    NOTIFY_TEST_TOKEN     = ""
    OPS_BOT_TOKEN         = ""
    OPS_BOT_TOKEN_ENABLED = ""
    POST_TO_GH            = ""
    POST_TO_SLACK         = ""
    SEND_TO_NOTIFY        = ""
    SLACK_WEBHOOK_URL     = ""
  }
}