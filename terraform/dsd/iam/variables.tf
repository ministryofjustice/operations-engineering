variable "github_token" {
  type        = string
  description = "Required by the GitHub Terraform provider"
  default     = ""
}

variable "cloud_platform_account_id" {
  sensitive   = true
  description = "The Account ID of the Cloud Platform AWS Account"
}

