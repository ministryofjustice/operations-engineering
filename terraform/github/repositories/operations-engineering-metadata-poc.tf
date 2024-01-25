module "operations-engineering-metadata-poc" {
  source = "github.com/ministryofjustice/operations-engineering-terraform-github-repositories?ref=0.0.2"

  name             = "operations-engineering-metadata-poc"
  application_name = "operations-engineering-metadata-poc"
  description      = "PoC For Cross Identification Between MoJ Services"
  tags = {
    Team  = "operations-engineering"
    Phase = "poc"
  }
}