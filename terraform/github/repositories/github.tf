module "github" {
  source  = "ministryofjustice/repository/github"
  version = "0.0.3"

  name             = ".github"
  application_name = ".github"
  description      = "Default organisational policies for the Ministry of Justice"
}