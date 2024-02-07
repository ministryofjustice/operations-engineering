terraform {
  backend "s3" {
    acl            = "private"
    bucket         = "cloud-platform-fad89ef06d68fdbc1928cb37acd8fc9f"
    dynamodb_table = "github-repos-prod-state-lock-table"
    encrypt        = true
    key            = "terraform/github-repos/operations-engineering-prod/terraform.tfstate"
    region         = "eu-west-2"
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