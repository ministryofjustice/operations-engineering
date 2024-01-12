module "repository" {
  source  = "mineiros-io/repository/github"
  version = "~> 0.18.0"

  name               = "test-repo-levg"
  license_template   = "mit"
}