module "repository" {
  source  = "github.com/ministryofjustice/operations-engineering-terraform-github-repositories"

  name = "test-repo-levg"
  description = "This repo was created using terraform by the operations engineering team"
}