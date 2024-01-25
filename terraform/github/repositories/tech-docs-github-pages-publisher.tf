module "tech-docs-github-pages-publisher" {
  source = "github.com/ministryofjustice/operations-engineering-terraform-github-repositories?ref=0.0.2"

  name             = "tech-docs-github-pages-publisher"
  application_name = "tech-docs-github-pages-publisher"
  description      = "Docker image to publish MoJ documentation repositories as github pages sites"
  homepage_url     = "https://hub.docker.com/r/ministryofjustice/tech-docs-github-pages-publisher"
  tags = {
    Team  = "operations-engineering"
    Phase = "production"
  }
}