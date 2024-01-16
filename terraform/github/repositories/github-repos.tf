locals {
  operations_engineering_repositories = {

    "test-repository-levg" = {
      name            = "test-repository-levg"
      application_name = "test-repository-levg"
      description = "this repository was create by terraform managed by operations-engineering team"
      topics = ["github", "terraform", "operations-engineering"]
      tags = {
        Team = "operations-engineering"
        Phase = "POC"
      }
    }

    "test-repository-levg2" = {
      name            = "test-repository-levg2"
      application_name = "test-repository-levg2"
      description = "this repository was create by terraform managed by operations-engineering team"
      topics = ["github", "terraform", "operations-engineering"]
      tags = {
        Team = "operations-engineering"
        Phase = "POC"
      }
    }

    "test-repository-levg3" = {
      name            = "test-repository-levg3"
      application_name = "test-repository-levg3"
      description = "this repository was create by terraform managed by operations-engineering team"
      topics = ["github", "terraform", "operations-engineering"]
      tags = {
        Team = "operations-engineering"
        Phase = "POC"
      }
    }

  }
}

module "operations_engineering_repositories" {
  source = "github.com/ministryofjustice/operations-engineering-terraform-github-repositories"

  for_each = { for repository in local.operations_engineering_repositories : repository.name => repository }

  name = each.value.name
  application_name = each.value.application_name
  description = each.value.description
  topics = each.value.topics
  tags = each.value.tags
}