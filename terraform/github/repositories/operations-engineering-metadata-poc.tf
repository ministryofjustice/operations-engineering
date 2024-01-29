module "operations-engineering-metadata-poc" {
  source  = "ministryofjustice/repository/github"
  version = "0.0.3"

  name             = "operations-engineering-metadata-poc"
  application_name = "operations-engineering-metadata-poc"
  description      = "PoC For Cross Identification Between MoJ Services"
}