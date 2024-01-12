module "repository" {
  source  = "github.com/ministryofjustice/data-platform/tree/main/terraform/github/modules/repository"

  name = "test-repo-levg"
  description = "This repo was created using terraform by the operations engineering team"
}