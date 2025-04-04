terraform {
  backend "s3" {
    acl     = "private"
    bucket  = "auth0-tfstate-bucket"
    encrypt = true
    key     = "terraform/auth0/operations-engineering-test/terraform.tfstate"
    region  = "eu-west-2"
  }
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "5.31.0"
    }
    auth0 = {
      source  = "auth0/auth0"
      version = "1.1.2"
    }
  }
  required_version = "~> 1.6"
}

provider "auth0" {
  domain        = var.auth0_domain_test
  client_id     = var.auth0_client_id_test
  client_secret = var.auth0_client_secret_test
}
