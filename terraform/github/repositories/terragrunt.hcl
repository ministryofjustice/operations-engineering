remote_state {
  backend = "s3"
  generate = {
    path      = "backend.tf"
    if_exists = "overwrite_terragrunt"
  }
  config = {
    bucket = "cloud-platform-fad89ef06d68fdbc1928cb37acd8fc9f"

    key = "terraform/github-repos/operations-engineering-prod/terraform.tfstate"
    region         = "eu-west-2"
    encrypt        = true
    dynamodb_table = "cp-1aaae79e1c9a29a8"
    acl            = "private"
    skip_bucket_update = true
  }
}
