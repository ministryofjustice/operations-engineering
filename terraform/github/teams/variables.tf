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


variable "cloud_optimisation_and_accountability_team_id" {
  description = "cloud-optimisation-and-accountability team id"
  type        = string
}
