terraform {
  backend "s3" {
    acl     = "private"
    bucket  = "cloud-platform-91d489cf0077d4786792c06920fa7f61"
    encrypt = true
    key     = "terraform/github-repos/operations-engineering-dev/terraform.tfstate"
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
  # owner = "ministryofjustice-test"
}