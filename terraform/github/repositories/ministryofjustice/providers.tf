terraform {
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
