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

variable "azure_client_secret_test" {
  description = "Test client secret for azure connection"
  type        = string
  default     = env("TF_VAR_auth0_azure_client_secret_test")
  sensitive   = true
}

variable "azure_client_id_test" {
  description = "Test client ID for azure connection"
  type        = string
  default     = env("TF_VAR_auth0_azure_client_id_test")
  sensitive   = true
}