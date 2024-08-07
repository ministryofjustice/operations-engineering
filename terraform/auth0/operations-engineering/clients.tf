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
  description                           = null
  encryption_key                        = {}
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

resource "auth0_client" "moj_auth0_azure_prod" {
  allowed_clients                       = []
  allowed_logout_urls                   = ["http://*.cloud-platform.service.justice.gov.uk", "http://127.0.0.1:4567", "http://127.0.0.1/", "http://localhost:4567", "http://localhost", "http://0.0.0.0", "https://dev.join-github.service.justice.gov.uk/", "https://join-github.service.justice.gov.uk/", "http://dev.join-github.service.justice.gov.uk/", "http://join-github.service.justice.gov.uk/"]
  allowed_origins                       = []
  app_type                              = "regular_web"
  callbacks                             = ["http://*.cloud-platform.service.justice.gov.uk/auth/callback", "https://localhost:4567/auth/callback", "http://127.0.0.1:4567/auth/callback", "http://127.0.0.1/auth/callback", "http://localhost:4567/auth/callback", "http://0.0.0.0:4567/auth/callback", "http://localhost/auth/callback", "https://dev.join-github.service.justice.gov.uk/auth/callback", "https://join-github.service.justice.gov.uk/auth/callback", "http://dev.join-github.service.justice.gov.uk/auth/callback", "http://join-github.service.justice.gov.uk/auth/callback"]
  client_aliases                        = []
  client_metadata                       = {}
  cross_origin_auth                     = false
  cross_origin_loc                      = null
  custom_login_page                     = null
  custom_login_page_on                  = true
  description                           = "This is used for ALL our authentication between Auth0 and Azure AD: Join GitHub dev, Join GitHub prod, ministryofjustice-test SSO."
  encryption_key                        = {}
  form_template                         = null
  grant_types                           = ["authorization_code", "implicit", "refresh_token", "client_credentials"]
  initiate_login_uri                    = null
  is_first_party                        = true
  is_token_endpoint_ip_header_trusted   = false
  logo_uri                              = null
  name                                  = "moj-auth0-azure-prod"
  oidc_backchannel_logout_urls          = []
  oidc_conformant                       = true
  organization_require_behavior         = "no_prompt"
  organization_usage                    = null
  require_pushed_authorization_requests = false
  sso                                   = false
  sso_disabled                          = false
  web_origins                           = ["http://*.cloud-platform.service.justice.gov.uk", "http://127.0.0.1:4567", "http://localhost:4567", "http://localhost", "http://127.0.0.1/", "http://0.0.0.0:4567", "https://dev.join-github.service.justice.gov.uk/", "https://join-github.service.justice.gov.uk/"]
  jwt_configuration {
    alg                 = "RS256"
    lifetime_in_seconds = 35994
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
  description                           = null
  encryption_key                        = {}
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
  description                           = null
  encryption_key                        = {}
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

resource "auth0_client" "default_app" {
  allowed_clients                       = []
  allowed_logout_urls                   = []
  allowed_origins                       = []
  app_type                              = null
  callbacks                             = []
  client_aliases                        = []
  client_metadata                       = {}
  cross_origin_auth                     = false
  cross_origin_loc                      = null
  custom_login_page                     = null
  custom_login_page_on                  = true
  description                           = null
  encryption_key                        = {}
  form_template                         = null
  grant_types                           = ["authorization_code", "implicit", "refresh_token", "client_credentials"]
  initiate_login_uri                    = null
  is_first_party                        = true
  is_token_endpoint_ip_header_trusted   = false
  logo_uri                              = null
  name                                  = "Default App"
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
    idle_token_lifetime          = 1296000
    infinite_idle_token_lifetime = true
    infinite_token_lifetime      = true
    leeway                       = 0
    rotation_type                = "non-rotating"
    token_lifetime               = 2592000
  }
}

resource "auth0_client" "operations_engineering_standards_report" {
  allowed_clients                       = []
  allowed_logout_urls                   = ["http://127.0.0.1:4567", "http://127.0.0.1/", "http://localhost:4567", "http://localhost", "http://operations-engineering-reports.cloud-platform.service.justice.gov.uk", "http://operations-engineering-reports-dev.cloud-platform.service.justice.gov.uk", "http://operations-engineering-reports-prod.cloud-platform.service.justice.gov.uk"]
  allowed_origins                       = []
  app_type                              = "regular_web"
  callbacks                             = ["http://127.0.0.1:4567/callback", "http://127.0.0.1:4567/auth/callback", "http://localhost:4567/auth/callback", "https://localhost:4567/auth/callback", "http://127.0.0.1/callback", "http://localhost:4567/callback", "http://localhost/callback", "http://operations-engineering-reports.cloud-platform.service.justice.gov.uk/callback", "http://operations-engineering-reports-dev.cloud-platform.service.justice.gov.uk/callback", "http://operations-engineering-reports-prod.cloud-platform.service.justice.gov.uk/callback"]
  client_aliases                        = []
  client_metadata                       = {}
  cross_origin_auth                     = false
  cross_origin_loc                      = null
  custom_login_page                     = null
  custom_login_page_on                  = true
  description                           = null
  encryption_key                        = {}
  form_template                         = null
  grant_types                           = ["authorization_code", "implicit", "refresh_token"]
  initiate_login_uri                    = null
  is_first_party                        = true
  is_token_endpoint_ip_header_trusted   = false
  logo_uri                              = null
  name                                  = "Operations-Engineering-Standards-Report"
  oidc_backchannel_logout_urls          = []
  oidc_conformant                       = true
  organization_require_behavior         = null
  organization_usage                    = null
  require_pushed_authorization_requests = false
  sso                                   = false
  sso_disabled                          = false
  web_origins                           = ["http://127.0.0.1:4567", "http://localhost:4567", "http://localhost", "http://127.0.0.1/", "http://operations-engineering-reports.cloud-platform.service.justice.gov.uk", "http://operations-engineering-reports-dev.cloud-platform.service.justice.gov.uk", "http://operations-engineering-reports-prod.cloud-platform.service.justice.gov.uk"]
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

resource "auth0_client" "prod_auth0managementapi" {
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
  description                           = null
  encryption_key                        = {}
  form_template                         = null
  grant_types                           = ["client_credentials"]
  initiate_login_uri                    = null
  is_first_party                        = true
  is_token_endpoint_ip_header_trusted   = false
  logo_uri                              = null
  name                                  = "Prod-Auth0ManagementAPI"
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

resource "auth0_client" "test_operations_engineering_moj_github_login" {
  allowed_clients                       = []
  allowed_logout_urls                   = []
  allowed_origins                       = []
  app_type                              = "spa"
  callbacks                             = ["http://localhost:4567"]
  client_aliases                        = []
  client_metadata                       = {}
  cross_origin_auth                     = false
  cross_origin_loc                      = null
  custom_login_page                     = null
  custom_login_page_on                  = true
  description                           = null
  encryption_key                        = {}
  form_template                         = null
  grant_types                           = ["authorization_code", "implicit", "refresh_token"]
  initiate_login_uri                    = null
  is_first_party                        = true
  is_token_endpoint_ip_header_trusted   = false
  logo_uri                              = null
  name                                  = "test-operations-engineering-moj-github-login"
  oidc_backchannel_logout_urls          = []
  oidc_conformant                       = true
  organization_require_behavior         = null
  organization_usage                    = null
  require_pushed_authorization_requests = false
  sso                                   = false
  sso_disabled                          = false
  web_origins                           = ["localhost:4567"]
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
    expiration_type              = "expiring"
    idle_token_lifetime          = 1296000
    infinite_idle_token_lifetime = false
    infinite_token_lifetime      = false
    leeway                       = 0
    rotation_type                = "rotating"
    token_lifetime               = 2592000
  }
}

resource "auth0_client" "github_enterprise_cloud" {
  allowed_clients                       = []
  allowed_logout_urls                   = []
  allowed_origins                       = []
  app_type                              = "sso_integration"
  callbacks                             = ["https://github.com/orgs/ministryofjustice-test/saml/consume"]
  client_aliases                        = []
  client_metadata                       = {}
  cross_origin_auth                     = false
  cross_origin_loc                      = null
  custom_login_page                     = null
  custom_login_page_on                  = true
  description                           = null
  encryption_key                        = {}
  form_template                         = null
  grant_types                           = ["authorization_code", "implicit", "refresh_token", "client_credentials"]
  initiate_login_uri                    = null
  is_first_party                        = true
  is_token_endpoint_ip_header_trusted   = false
  logo_uri                              = null
  name                                  = "GitHub Enterprise Cloud"
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
      audience                      = "https://github.com/orgs/ministryofjustice-test"
      authn_context_class_ref       = null
      binding                       = null
      create_upn_claim              = true
      destination                   = null
      digest_algorithm              = "sha256"
      include_attribute_name_format = true
      issuer                        = null
      lifetime_in_seconds           = 3600
      map_identities                = false
      map_unknown_claims_as_is      = false
      mappings = {
        email   = "emails"
        name    = "full_name"
        user_id = "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/nameidentifier"
      }
      name_identifier_format             = "urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress"
      name_identifier_probes             = ["http://schemas.xmlsoap.org/ws/2005/05/identity/claims/nameidentifier"]
      passthrough_claims_with_no_mapping = false
      recipient                          = null
      sign_response                      = false
      signature_algorithm                = "rsa-sha256"
      signing_cert                       = null
      typed_attributes                   = true
      logout {
        callback    = null
        slo_enabled = true
      }
    }
    sso_integration {
      name    = "github-enterprise-cloud"
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

resource "auth0_client" "api_explorer_application" {
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
  description                           = null
  encryption_key                        = {}
  form_template                         = null
  grant_types                           = ["client_credentials"]
  initiate_login_uri                    = null
  is_first_party                        = true
  is_token_endpoint_ip_header_trusted   = false
  logo_uri                              = null
  name                                  = "API Explorer Application"
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

resource "auth0_client" "operations_engineering_kpi_dashboard" {
  allowed_clients                       = []
  allowed_logout_urls                   = ["http://127.0.0.1:4567", "http://127.0.0.1/", "http://localhost:4567", "http://localhost", "http://operations-engineering-kpi-dashboard.cloud-platform.service.justice.gov.uk", "http://operations-engineering-kpi-dashboard-poc.cloud-platform.service.justice.gov.uk", "http://operations-engineering-kpi-dashboard-prod.cloud-platform.service.justice.gov.uk"]
  allowed_origins                       = []
  app_type                              = "regular_web"
  callbacks                             = ["http://127.0.0.1:4567/callback", "http://127.0.0.1:4567/auth/callback", "http://localhost:4567/auth/callback", "https://localhost:4567/auth/callback", "http://127.0.0.1/callback", "http://localhost:4567/callback", "http://localhost/callback", "http://operations-engineering-kpi-dashboard.cloud-platform.service.justice.gov.uk/callback", "http://operations-engineering-kpi-dashboard-poc.cloud-platform.service.justice.gov.uk/callback", "http://operations-engineering-kpi-dashboard-prod.cloud-platform.service.justice.gov.uk/callback"]
  client_aliases                        = []
  client_metadata                       = {}
  cross_origin_auth                     = false
  cross_origin_loc                      = null
  custom_login_page                     = null
  custom_login_page_on                  = true
  description                           = null
  form_template                         = null
  grant_types                           = ["authorization_code", "implicit", "refresh_token"]
  initiate_login_uri                    = null
  is_first_party                        = true
  is_token_endpoint_ip_header_trusted   = false
  logo_uri                              = null
  name                                  = "Operations-Engineering-KPI-Dashboard"
  oidc_backchannel_logout_urls          = []
  oidc_conformant                       = true
  organization_require_behavior         = null
  organization_usage                    = null
  require_pushed_authorization_requests = false
  sso                                   = false
  sso_disabled                          = false
  web_origins                           = ["http://127.0.0.1:4567", "http://localhost:4567", "http://localhost", "http://127.0.0.1/", "http://operations-engineering-kpi-dashboard.cloud-platform.service.justice.gov.uk", "http://operations-engineering-kpi-dashboard-poc.cloud-platform.service.justice.gov.uk", "http://operations-engineering-kpi-dashboard-prod.cloud-platform.service.justice.gov.uk"]
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

resource "auth0_client" "moj_microsoft_authentication_dev" {
  allowed_clients                       = []
  allowed_logout_urls                   = ["http://*.cloud-platform.service.justice.gov.uk", "http://127.0.0.1:4567", "http://127.0.0.1/", "http://localhost:4567", "http://localhost", "http://0.0.0.0", "https://dev.join-github.service.justice.gov.uk/", "http://dev.join-github.service.justice.gov.uk/"]
  allowed_origins                       = []
  app_type                              = "regular_web"
  callbacks                             = ["http://*.cloud-platform.service.justice.gov.uk/auth/callback", "https://localhost:4567/auth/callback", "http://127.0.0.1:4567/auth/callback", "http://127.0.0.1/auth/callback", "http://localhost:4567/auth/callback", "http://0.0.0.0:4567/auth/callback", "http://localhost/auth/callback", "https://dev.join-github.service.justice.gov.uk/auth/callback", "http://dev.join-github.service.justice.gov.uk/auth/callback"]
  client_aliases                        = []
  client_metadata                       = {}
  cross_origin_auth                     = false
  cross_origin_loc                      = null
  custom_login_page                     = null
  custom_login_page_on                  = true
  description                           = "This application should be used for any authentication to Microsoft tools required for development environments."
  encryption_key                        = {}
  form_template                         = null
  grant_types                           = ["authorization_code", "implicit", "refresh_token", "client_credentials"]
  initiate_login_uri                    = null
  is_first_party                        = true
  is_token_endpoint_ip_header_trusted   = false
  logo_uri                              = null
  name                                  = "MoJ Microsoft Authentication Dev"
  oidc_backchannel_logout_urls          = []
  oidc_conformant                       = true
  organization_require_behavior         = "no_prompt"
  organization_usage                    = null
  require_pushed_authorization_requests = false
  sso                                   = false
  sso_disabled                          = false
  web_origins                           = ["http://*.cloud-platform.service.justice.gov.uk", "http://127.0.0.1:4567", "http://localhost:4567", "http://localhost", "http://127.0.0.1/", "http://0.0.0.0:4567", "https://dev.join-github.service.justice.gov.uk/"]
  jwt_configuration {
    alg                 = "RS256"
    lifetime_in_seconds = 35994
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

resource "auth0_client" "moj_microsoft_authentication_prod" {
  allowed_clients                       = []
  allowed_logout_urls                   = ["http://*.cloud-platform.service.justice.gov.uk", "http://127.0.0.1:4567", "http://127.0.0.1/", "http://localhost:4567", "http://localhost", "http://0.0.0.0", "https://join-github.service.justice.gov.uk/", "http://join-github.service.justice.gov.uk/"]
  allowed_origins                       = []
  app_type                              = "regular_web"
  callbacks                             = ["http://*.cloud-platform.service.justice.gov.uk/auth/callback", "https://localhost:4567/auth/callback", "http://127.0.0.1:4567/auth/callback", "http://127.0.0.1/auth/callback", "http://localhost:4567/auth/callback", "http://0.0.0.0:4567/auth/callback", "http://localhost/auth/callback", "https://join-github.service.justice.gov.uk/auth/callback", "http://join-github.service.justice.gov.uk/auth/callback"]
  client_aliases                        = []
  client_metadata                       = {}
  cross_origin_auth                     = false
  cross_origin_loc                      = null
  custom_login_page                     = null
  custom_login_page_on                  = true
  description                           = "This application should be used for any authentication to Microsoft tools required for production environments."
  form_template                         = null
  grant_types                           = ["authorization_code", "implicit", "refresh_token", "client_credentials"]
  initiate_login_uri                    = null
  is_first_party                        = true
  is_token_endpoint_ip_header_trusted   = false
  logo_uri                              = null
  name                                  = "MoJ Microsoft Authentication Prod"
  oidc_backchannel_logout_urls          = []
  oidc_conformant                       = true
  organization_require_behavior         = "no_prompt"
  organization_usage                    = null
  require_pushed_authorization_requests = false
  sso                                   = false
  sso_disabled                          = false
  web_origins                           = ["http://*.cloud-platform.service.justice.gov.uk", "http://127.0.0.1:4567", "http://localhost:4567", "http://localhost", "http://127.0.0.1/", "http://0.0.0.0:4567", "https://join-github.service.justice.gov.uk/"]
  jwt_configuration {
    alg                 = "RS256"
    lifetime_in_seconds = 35994
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
