remote_state {
  backend = "s3"
  generate = {
    path      = "backend.tf"
    if_exists = "overwrite_terragrunt"
  }
  config = {
    bucket = "operations-engineering-test-terraform-state-bucket"

    key = "terraform/dsd/github_repositories/terraform.tfstate"
    region         = "eu-west-2"
    encrypt        = true
    acl            = "private"
  }
}
