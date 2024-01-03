terraform {
  backend "s3" {
    bucket = "cloud-platform-7a8908cb6aea78a104f6ff554c4db90b"
    region = "eu-west-2"
  }
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "5.31.0"
    }
    auth0 = {
      source  = "auth0/auth0"
      version = "1.1.1"
    }
  }
  required_version = "~> 1.6"
}
