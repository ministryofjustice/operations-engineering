variable "auth0_domain_test" {
  description = "value of the Auth0 domain"
  default     = ""
  type        = string
  sensitive   = true
}

variable "auth0_client_id_test" {
  description = "value of the Auth0 client id"
  default     = ""
  type        = string
  sensitive   = true
}

variable "auth0_client_secret_test" {
  description = "value of the Auth0 client secret"
  default     = ""
  type        = string
  sensitive   = true
}

variable "google_workspace_connection_client_id" {
  description = "Client ID value for the Google Workspace connection"
  type        = string
  sensitive   = true
}

variable "google_workspace_connection_secret" {
  description = "Client secret value for the Google Workspace connection"
  type        = string
  sensitive   = true
}

variable "github_application_client_id" {
  description = "Client ID value for the the GitHub Application in Auth0"
  type        = string
  sensitive   = true
}
