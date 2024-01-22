module "github" {
  source = "github.com/ministryofjustice/operations-engineering-terraform-github-repositories?ref=0.0.1"

  name             = ".github"
  application_name = ".github"
  description      = "Default organisational policies for the Ministry of Justice"
  topics           = []
  tags = {
    Team  = "operations-engineering"
    Phase = "production"
  }
}