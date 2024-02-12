module "operations-engineering-metadata-poc" {
  source  = "ministryofjustice/repository/github"
  version = "0.0.7"

  name        = "operations-engineering-metadata-poc"
  description = "PoC For Cross Identification Between MoJ Services"
  topics      = ["operations-engineering"]
  variables = {
    DEVELOPMENT_ECR_REGION     = var.ECR_REGION
    DEVELOPMENT_ECR_REPOSITORY = "operations-engineering/operations-engineering-metadata-poc-ecr"
    ECR_REGISTRY               = var.ECR_REGISTRY
  }
}