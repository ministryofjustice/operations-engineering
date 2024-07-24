module "operations-engineering-find-a-github-repository-owner" {
  source  = "ministryofjustice/repository/github"
  version = "1.1.1"

  name        = "operations-engineering-find-a-github-repository-owner"
  description = "Find Owners of GitHub Reposistories"
  topics      = ["operations-engineering"]

  team_access = {
    admin = [var.operations_engineering_team_id]
  }
}
