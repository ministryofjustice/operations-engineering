resource "auth0_connection" "google_workspace" {
  name                 = "google-workspace-connection"
  display_name         = "Google (Test)"
  is_domain_connection = false
  strategy             = "google-apps"
  show_as_button       = true
  options {
    client_id        = var.google_workspace_connection_client_id
    client_secret    = var.google_workspace_connection_secret
    domain           = "justice.gov.uk"
    tenant_domain    = "justice.gov.uk"
    api_enable_users = true
    scopes           = ["ext_profile", "basic_profile"]
    upstream_params = jsonencode({
      "screen_name" : {
        "alias" : "login_hint"
      }
    })
    set_user_root_attributes = "on_each_login"
  }
}
