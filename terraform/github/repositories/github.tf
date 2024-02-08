module "github" {
  source  = "ministryofjustice/repository/github"
  version = "0.0.6"

  name             = ".github"
  description      = "Default organisational policies for the Ministry of Justice"
  topics           = ["operations-engineering"]
}