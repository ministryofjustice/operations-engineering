terraform {
  backend "s3" {
    acl     = "private"
    bucket  = "operations-engineering-test-terraform-state-bucket"
    encrypt = true
    key     = "terraform/dsd/github_repositories/minstryofjustice/terraform.tfstate"
    region  = "eu-west-2"
  }
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "5.31.0"
    }
    github = {
      source  = "integrations/github"
      version = "~> 5.0"
    }
  }
  required_version = "~> 1.6"
}

provider "github" {
  token = var.github_token
  owner = "ministryofjustice"
}

provider "aws" {
  profile = "dsd_secret_manager_access_profile"
  region  = "eu-west-2"
}
