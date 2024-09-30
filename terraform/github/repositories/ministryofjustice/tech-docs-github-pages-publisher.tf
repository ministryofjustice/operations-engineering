module "tech-docs-github-pages-publisher" {
  source  = "ministryofjustice/repository/github"
  version = "1.2.0"

  name         = "tech-docs-github-pages-publisher"
  description  = "Docker image to publish MoJ documentation repositories as github pages sites"
  homepage_url = "https://hub.docker.com/r/ministryofjustice/tech-docs-github-pages-publisher"
  topics       = ["operations-engineering"]

  team_access = {
    admin = [var.operations_engineering_team_id]
  }
}
