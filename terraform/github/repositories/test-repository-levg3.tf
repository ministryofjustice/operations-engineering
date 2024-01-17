module "test-repository-levg3" {
  source = "github.com/ministryofjustice/operations-engineering-terraform-github-repositories"

  name = "test-repository-levg3"
  application_name = "test-repository-levg3"
  description = "this repository was create by terraform managed by operations-engineering team"
  topics = ["github", "terraform", "operations-engineering"]
  tags = {
    Team = "operations-engineering"
    Phase = "POC"
    }
}