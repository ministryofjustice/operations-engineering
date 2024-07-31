terraform {
  backend "s3" {
    acl     = "private"
    bucket  = "operations-engineering-test-terraform-state-bucket"
    encrypt = true
    key     = "terraform/dsd/github_repositories/ministryofjustice-test/terraform.tfstate"
    region  = "eu-west-2"
  }
  required_providers {
    github = {
      source  = "integrations/github"
      version = "~> 5.0"
    }
  }
  required_version = "~> 1.6"
}

provider "github" {
  token = var.github_token
  owner = "ministryofjustice-test"
}
