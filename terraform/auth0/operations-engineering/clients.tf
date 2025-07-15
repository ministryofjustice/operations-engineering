resource "auth0_client" "pagerduty" {
  allowed_clients                       = []
  allowed_logout_urls                   = []
  allowed_origins                       = []
  app_type                              = "sso_integration"
  callbacks                             = ["https://moj-digital-tools.pagerduty.com/sso/saml/consume"]
  client_aliases                        = []
  client_metadata                       = {}
  cross_origin_auth                     = false
  cross_origin_loc                      = null
  custom_login_page                     = null
  custom_login_page_on                  = true
  description                           = "This enables Auth0 SSO via GitHub to login to PagerDuty."
  form_template                         = null
  grant_types                           = ["authorization_code", "implicit", "refresh_token", "client_credentials"]
  initiate_login_uri                    = null
  is_first_party                        = true
  is_token_endpoint_ip_header_trusted   = false
  logo_uri                              = null
  name                                  = "PagerDuty"
  oidc_backchannel_logout_urls          = []
  oidc_conformant                       = true
  organization_require_behavior         = null
  organization_usage                    = null
  require_pushed_authorization_requests = false
  sso                                   = false
  sso_disabled                          = false
  web_origins                           = []
  addons {
    samlp {
      audience                           = "https://moj-digital-tools.pagerduty.com"
      authn_context_class_ref            = null
      binding                            = null
      create_upn_claim                   = true
      destination                        = null
      digest_algorithm                   = "sha1"
      include_attribute_name_format      = true
      issuer                             = null
      lifetime_in_seconds                = 3600
      map_identities                     = true
      map_unknown_claims_as_is           = false
      mappings                           = {}
      name_identifier_format             = "urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress"
      name_identifier_probes             = ["http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress"]
      passthrough_claims_with_no_mapping = true
      recipient                          = null
      sign_response                      = false
      signature_algorithm                = "rsa-sha1"
      signing_cert                       = null
      typed_attributes                   = true
      logout {
        callback    = null
        slo_enabled = true
      }
    }
    sso_integration {
      name    = "pagerduty"
      version = null
    }
  }
  jwt_configuration {
    alg                 = "RS256"
    lifetime_in_seconds = 36000
    scopes              = {}
    secret_encoded      = false
  }
  refresh_token {
    expiration_type              = "non-expiring"
    idle_token_lifetime          = 1296000
    infinite_idle_token_lifetime = true
    infinite_token_lifetime      = true
    leeway                       = 0
    rotation_type                = "non-rotating"
    token_lifetime               = 2592000
  }
}

resource "auth0_client" "dockersso" {
  allowed_clients                       = []
  allowed_logout_urls                   = []
  allowed_origins                       = []
  app_type                              = "regular_web"
  callbacks                             = ["https://login.docker.com/login/callback?connection=samlp-ministryofjustice"]
  client_aliases                        = []
  client_metadata                       = {}
  cross_origin_auth                     = false
  cross_origin_loc                      = null
  custom_login_page                     = null
  custom_login_page_on                  = true
  description                           = "This enables Auth0 SSO via Github to login to Docker."
  form_template                         = null
  grant_types                           = ["authorization_code", "implicit", "refresh_token", "client_credentials"]
  initiate_login_uri                    = null
  is_first_party                        = true
  is_token_endpoint_ip_header_trusted   = false
  logo_uri                              = null
  name                                  = "DockerSSO"
  oidc_backchannel_logout_urls          = []
  oidc_conformant                       = true
  organization_require_behavior         = null
  organization_usage                    = null
  require_pushed_authorization_requests = false
  sso                                   = false
  sso_disabled                          = false
  web_origins                           = []
  addons {
  }
  jwt_configuration {
    alg                 = "RS256"
    lifetime_in_seconds = 36000
    scopes              = {}
    secret_encoded      = false
  }
  native_social_login {
    apple {
      enabled = false
    }
    facebook {
      enabled = false
    }
  }
  refresh_token {
    expiration_type              = "non-expiring"
    idle_token_lifetime          = 2592000
    infinite_idle_token_lifetime = true
    infinite_token_lifetime      = true
    leeway                       = 0
    rotation_type                = "non-rotating"
    token_lifetime               = 31557600
  }
}

resource "auth0_client" "terraform_provider_auth0" {
  allowed_clients                       = []
  allowed_logout_urls                   = []
  allowed_origins                       = []
  app_type                              = "non_interactive"
  callbacks                             = []
  client_aliases                        = []
  client_metadata                       = {}
  cross_origin_auth                     = false
  cross_origin_loc                      = null
  custom_login_page                     = null
  custom_login_page_on                  = true
  description                           = "This enables Terraform to manage Auth0 in code via the operations-engineering repository."
  form_template                         = null
  grant_types                           = ["client_credentials"]
  initiate_login_uri                    = null
  is_first_party                        = true
  is_token_endpoint_ip_header_trusted   = false
  logo_uri                              = null
  name                                  = "Terraform Provider Auth0"
  oidc_backchannel_logout_urls          = []
  oidc_conformant                       = true
  organization_require_behavior         = null
  organization_usage                    = null
  require_pushed_authorization_requests = false
  sso                                   = false
  sso_disabled                          = false
  web_origins                           = []
  jwt_configuration {
    alg                 = "RS256"
    lifetime_in_seconds = 36000
    scopes              = {}
    secret_encoded      = false
  }
  refresh_token {
    expiration_type              = "non-expiring"
    idle_token_lifetime          = 2592000
    infinite_idle_token_lifetime = true
    infinite_token_lifetime      = true
    leeway                       = 0
    rotation_type                = "non-rotating"
    token_lifetime               = 31557600
  }
}

resource "auth0_client" "kpi_dashboard" {
  allowed_clients                       = []
  allowed_logout_urls                   = []
  allowed_origins                       = []
  app_type                              = "regular_web"
  callbacks                             = ["https://kpi-dashboard.cloud-platform.service.justice.gov.uk/oidc/idp/callback", "http://0.0.0.0:4567/oidc/idp/callback", "http://localhost:4567/oidc/idp/callback", "http://127.0.0.1:4567/oidc/idp/callback"]
  client_aliases                        = []
  client_metadata                       = {}
  cross_origin_auth                     = false
  cross_origin_loc                      = null
  custom_login_page                     = null
  custom_login_page_on                  = true
  description                           = "This enables GitHub SSO login to the KPI Dashboard."
  form_template                         = null
  grant_types                           = ["authorization_code", "implicit", "refresh_token"]
  initiate_login_uri                    = null
  is_first_party                        = true
  is_token_endpoint_ip_header_trusted   = false
  logo_uri                              = null
  name                                  = "KPI Dashboard"
  oidc_backchannel_logout_urls          = []
  oidc_conformant                       = true
  organization_require_behavior         = null
  organization_usage                    = null
  require_pushed_authorization_requests = false
  sso                                   = false
  sso_disabled                          = false
  web_origins                           = ["https://kpi-dashboard.cloud-platform.service.justice.gov.uk", "http://0.0.0.0:4567", "http://localhost:4567", "http://127.0.0.1:4567"]
  jwt_configuration {
    alg                 = "RS256"
    lifetime_in_seconds = 36000
    scopes              = {}
    secret_encoded      = false
  }
  native_social_login {
    apple {
      enabled = false
    }
    facebook {
      enabled = false
    }
  }
  refresh_token {
    expiration_type              = "non-expiring"
    idle_token_lifetime          = 1296000
    infinite_idle_token_lifetime = true
    infinite_token_lifetime      = true
    leeway                       = 0
    rotation_type                = "non-rotating"
    token_lifetime               = 2592000
  }
}

resource "auth0_client" "github" {
  allowed_clients                       = []
  allowed_logout_urls                   = []
  allowed_origins                       = []
  app_type                              = "regular_web"
  callbacks                             = ["https://github.com/orgs/ministryofjustice/saml/consume", "https://github.com/orgs/moj-analytical-services/saml/consume"]
  client_aliases                        = []
  client_metadata                       = {}
  cross_origin_auth                     = true
  cross_origin_loc                      = null
  custom_login_page                     = null
  custom_login_page_on                  = true
  description                           = "Web application to SSO into ministryofjustice or moj-analytical-services GitHub Organisations"
  form_template                         = null
  grant_types                           = ["authorization_code", "implicit", "refresh_token", "client_credentials"]
  initiate_login_uri                    = null
  is_first_party                        = true
  is_token_endpoint_ip_header_trusted   = false
  logo_uri                              = null
  name                                  = "GitHub"
  oidc_conformant                       = true
  organization_require_behavior         = "no_prompt"
  organization_usage                    = null
  require_pushed_authorization_requests = false
  sso                                   = false
  sso_disabled                          = false
  web_origins                           = []
  jwt_configuration {
    alg                 = "RS256"
    lifetime_in_seconds = 36000
    scopes              = {}
    secret_encoded      = false
  }
  native_social_login {
    apple {
      enabled = false
    }
    facebook {
      enabled = false
    }
  }
  refresh_token {
    expiration_type              = "non-expiring"
    idle_token_lifetime          = 2592000
    infinite_idle_token_lifetime = true
    infinite_token_lifetime      = true
    leeway                       = 0
    rotation_type                = "non-rotating"
    token_lifetime               = 31557600
  }
  addons {
    samlp {
      mappings = {
        user_id = "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/nameidentifier"
        email   = "emails"
        name    = "full_name"
      }
      passthrough_claims_with_no_mapping = false
      map_identities                     = false
      signature_algorithm                = "rsa-sha256"
      digest_algorithm                   = "sha256"
      name_identifier_probes             = ["http://schemas.xmlsoap.org/ws/2005/05/identity/claims/nameidentifier"]
    }
  }
}
