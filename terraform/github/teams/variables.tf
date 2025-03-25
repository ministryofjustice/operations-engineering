variable "github_token" {
  type        = string
  description = "Required by the GitHub Terraform provider"
  default     = ""
}


variable "ops_eng_support_members" {
  description = "List of GitHub usernames for operations-engineering-support team members"
  type        = list(string)
  default = [
    "andyrogers1973",
  ]
}
