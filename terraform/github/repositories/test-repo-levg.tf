module "test-repo-levg" {
  source = "github.com/ministryofjustice/terraform-github-repository?ref=provider-config"
  providers = var.ministryofjustice-test_provider_mapping

  name             = "test-repo-levg"
  application_name = "test-repo-levg"
  description      = "test repo"
}