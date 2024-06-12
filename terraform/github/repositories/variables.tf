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

variable "module_version" {
  type        = string
  description = "Version of github repository Terraform module"
  default     = "1.0.0"
}
