terraform {
  backend "s3" {
    acl            = "private"
    bucket         = "cloud-platform-fad89ef06d68fdbc1928cb37acd8fc9f"
    dynamodb_table = "cp-1aaae79e1c9a29a8"
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


provider "github" {
  alias = "ministryofjustice-test"
  token = var.github_token
  owner = "ministryofjustice-test"
}

provider "aws" {
  profile = "dsd_secret_manager_access_profile"
  region  = "eu-west-2"
}

moved {
  from = module.ministryofjustice.module.operations-engineering-kpi-dashboard-poc.github_branch_protection.default
  to   = module.ministryofjustice.module.operations-engineering-kpi-dashboard.github_branch_protection.default
}

moved {
  from = module.ministryofjustice.module.operations-engineering-kpi-dashboard-poc.github_repository.default
  to   = module.ministryofjustice.module.operations-engineering-kpi-dashboard.github_repository.default
}

moved {
  from = module.ministryofjustice.module.operations-engineering-kpi-dashboard-poc.github_repository_tag_protection.default
  to   = module.ministryofjustice.module.operations-engineering-kpi-dashboard.github_repository_tag_protection.default
}

moved {
  from = module.ministryofjustice.module.operations-engineering-kpi-dashboard-poc.github_team_repository.admin["4192115"]
  to   = module.ministryofjustice.module.operations-engineering-kpi-dashboard.github_team_repository.admin["4192115"]
}
