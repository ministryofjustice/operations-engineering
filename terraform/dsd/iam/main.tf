terraform {
  backend "s3" {
    acl            = "private"
    bucket         = "cloud-platform-d9c72789e891183c1ea471e06868ae09"
    dynamodb_table = "cp-98dabf78e72d7e22"
    encrypt        = true
    key            = "terraform/dsd/iam/terraform.tfstate"
    region         = "eu-west-2"
    # profile        = "state_profile"
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

# provider "aws" {
#   profile = "infra_profile"
#   region  = "eu-west-2"
# }