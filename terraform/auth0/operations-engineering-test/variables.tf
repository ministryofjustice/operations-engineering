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

variable "terraform_provider_auth0_encryption_key" {
  description = "Encryption key value for terraform provider auth0"
  type        = string
  default     = env("TF_VAR_terraform_provider_auth0_encryption_key")
  sensitive   = true
}

variable "default_app_encryption_key" {
  description = "Encryption key value for the default app"
  type        = string
  default     = env("TF_VAR_default_app_encryption_key")
  sensitive   = true
}
