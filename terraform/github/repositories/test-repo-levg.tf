module "test-repo-levg" {
  source = "github.com/ministryofjustice/terraform-github-repository?ref=provider-config"
  providers = {
    github.organisation = github.ministryofjustice-test
  }

  name             = "test-repo-levg"
  application_name = "test-repo-levg"
  description      = "test repo"
}