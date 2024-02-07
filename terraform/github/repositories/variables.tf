variable "github_token" {
  type        = string
  description = "Required by the GitHub Terraform provider"
  default     = ""
}

variable "ECR_REGION" {
  type        = string
  description = "Region of ECR repositories"
  default     = "eu-west-2"
}

variable "ECR_REGISTRY" {
  type        = string
  description = "Registry of ECR repositories"
  default     = "754256621582.dkr.ecr.eu-west-2.amazonaws.com"
}

variable "ministryofjustice-test_provider_mapping" {
  type = map(object({
    token = string
    owner = string
  }))
  description = "maps local github module provider to ministryofjustice-test provider alias"
  default = {
    github = github.ministryofjustice-test
  }
}