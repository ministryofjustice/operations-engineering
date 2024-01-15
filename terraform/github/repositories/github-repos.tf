module "repository" {

  source = "github.com/ministryofjustice/operations-engineering-terraform-github-repositories"

  application_name = "test-app-levg"
  description = "this repository was create by terraform managed by operations-engineering team"
  name = "test-repository-levg"
  tags = {
    Team = "operations-engineering"
    Phase = "POC"
  }
  topics = ["github", "terraform", "operations-engineering"]
}