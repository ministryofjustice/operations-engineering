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

variable "default_app_name" {
  description = "Test variable for a name value"
  default     = env("TF_VAR_default_app_name")
  type        = string
  sensitive   = true
}
