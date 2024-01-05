variable "auth0_domain" {
  description = "value of the Auth0 domain"
  default     = ""
  type        = string
  sensitive   = true
}

variable "auth0_client_id" {
  description = "value of the Auth0 client id"
  default     = ""
  type        = string
  sensitive   = true
}

variable "auth0_client_secret" {
  description = "value of the Auth0 client secret"
  default     = ""
  type        = string
  sensitive   = true
}
