resource "auth0_connection" "google_workspace" {
  name                 = "google-workspace-connection"
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

resource "auth0_connection" "google_oauth2" {
  display_name         = null
  is_domain_connection = false
  metadata             = {}
  name                 = "google-oauth2"
  realms               = ["google-oauth2"]
  show_as_button       = null
  strategy             = "google-oauth2"
  options {
    adfs_server                            = null
    allowed_audiences                      = []
    api_enable_users                       = false
    app_id                                 = null
    auth_params                            = {}
    authorization_endpoint                 = null
    brute_force_protection                 = false
    client_id                              = null
    client_secret                          = null # sensitive
    community_base_url                     = null
    configuration                          = null # sensitive
    custom_scripts                         = {}
    debug                                  = false
    digest_algorithm                       = null
    disable_cache                          = false
    disable_self_service_change_password   = false
    disable_sign_out                       = false
    disable_signup                         = false
    discovery_url                          = null
    domain                                 = null
    domain_aliases                         = []
    enable_script_context                  = false
    enabled_database_customization         = false
    entity_id                              = null
    fed_metadata_xml                       = null
    fields_map                             = null
    forward_request_info                   = false
    from                                   = null
    gateway_url                            = null
    icon_url                               = null
    identity_api                           = null
    import_mode                            = false
    ips                                    = []
    issuer                                 = null
    jwks_uri                               = null
    key_id                                 = null
    map_user_id_to_id                      = false
    max_groups_to_retrieve                 = null
    messaging_service_sid                  = null
    metadata_url                           = null
    metadata_xml                           = null
    name                                   = null
    non_persistent_attrs                   = []
    password_policy                        = null
    ping_federate_base_url                 = null
    pkce_enabled                           = false
    protocol_binding                       = null
    provider                               = null
    request_template                       = null
    requires_username                      = false
    scopes                                 = ["email", "profile"]
    scripts                                = {}
    set_user_root_attributes               = null
    should_trust_email_verified_connection = null
    sign_in_endpoint                       = null
    sign_out_endpoint                      = null
    sign_saml_request                      = false
    signature_algorithm                    = null
    signing_cert                           = null
    strategy_version                       = 0
    subject                                = null
    syntax                                 = null
    team_id                                = null
    template                               = null
    tenant_domain                          = null
    token_endpoint                         = null
    twilio_sid                             = null
    twilio_token                           = null # sensitive
    type                                   = null
    upstream_params                        = null
    use_cert_auth                          = false
    use_kerberos                           = false
    use_wsfed                              = false
    user_id_attribute                      = null
    userinfo_endpoint                      = null
    waad_common_endpoint                   = false
    waad_protocol                          = null
  }
}
