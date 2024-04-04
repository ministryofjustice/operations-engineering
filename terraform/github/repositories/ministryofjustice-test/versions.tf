terraform {
  required_version = "~> 1.6"
  required_providers {
    github = {
      version = "~> 5.0"
      source  = "integrations/github"
    }
  }
}