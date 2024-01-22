variable "github_token" {
  type        = string
  description = "Required by the GitHub Terraform provider"
  default     = ""
}

variable "module_version" {
  type        = string
  description = "version of github repository terraform module to use"
  default     = "0.0.1"
}