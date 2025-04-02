terraform {
  backend "s3" {
    acl     = "private"
    bucket  = "github-repos-tfstate-bucket"
    encrypt = true
    key     = "terraform/github-repos/operations-engineering-prod/terraform.tfstate"
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


provider "github" {
  alias = "ministryofjustice-test"
  token = var.github_token
  owner = "ministryofjustice-test"
}
