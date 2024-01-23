module "github" {
  source = "github.com/ministryofjustice/operations-engineering-terraform-github-repositories?ref=0.0.2"

  name             = ".github"
  application_name = ".github"
  description      = "Default organisational policies for the Ministry of Justice"
  tags = {
    Team  = "operations-engineering"
    Phase = "production"
  }
}