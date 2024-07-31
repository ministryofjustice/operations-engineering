
resource "auth0_tenant" "tenant" {
  allow_organization_name_in_authentication_api = false
  allowed_logout_urls                           = []
  customize_mfa_in_postlogin_action             = false
  default_audience                              = null
  default_directory                             = null
  default_redirection_uri                       = null
  enabled_locales                               = ["en"]
  friendly_name                                 = null
  idle_session_lifetime                         = 72
  picture_url                                   = null
  sandbox_version                               = "12"
  session_lifetime                              = 168
  support_email                                 = null
  support_url                                   = null
  flags {
    allow_legacy_delegation_grant_types    = false
    allow_legacy_ro_grant_types            = false
    allow_legacy_tokeninfo_endpoint        = false
    dashboard_insights_view                = false
    dashboard_log_streams_next             = false
    disable_clickjack_protection_headers   = false
    disable_fields_map_fix                 = false
    disable_management_api_sms_obfuscation = false
    enable_adfs_waad_email_verification    = false
    enable_apis_section                    = false
    enable_client_connections              = false
    enable_custom_domain_in_emails         = false
    enable_dynamic_client_registration     = false
    enable_idtoken_api2                    = false
    enable_legacy_logs_search_v2           = false
    enable_legacy_profile                  = false
    enable_pipeline2                       = false
    enable_public_signup_user_exists_error = false
    mfa_show_factor_list_on_enrollment     = false
    no_disclose_enterprise_connections     = false
    require_pushed_authorization_requests  = false
    revoke_refresh_token_grant             = false
    use_scope_descriptions_for_consent     = false
  }
  session_cookie {
    mode = null
  }
  sessions {
    oidc_logout_prompt_enabled = false
  }
}

resource "auth0_resource_server" "auth0_management_api" {
  allow_offline_access                            = false
  enforce_policies                                = null
  identifier                                      = "https://operations-engineering.eu.auth0.com/api/v2/"
  name                                            = "Auth0 Management API"
  signing_alg                                     = "RS256"
  signing_secret                                  = null
  skip_consent_for_verifiable_first_party_clients = false
  token_dialect                                   = null
  token_lifetime                                  = 360
  token_lifetime_for_web                          = 7200
  verification_location                           = null
}

resource "auth0_attack_protection" "attack_protection" {
  breached_password_detection {
    admin_notification_frequency = []
    enabled                      = false
    method                       = "standard"
    shields                      = []
    pre_user_registration {
      shields = []
    }
  }
  brute_force_protection {
    allowlist    = []
    enabled      = true
    max_attempts = 10
    mode         = "count_per_identifier_and_ip"
    shields      = ["block", "user_notification"]
  }
  suspicious_ip_throttling {
    allowlist = []
    enabled   = true
    shields   = ["admin_notification", "block"]
    pre_login {
      max_attempts = 100
      rate         = 864000
    }
    pre_user_registration {
      max_attempts = 50
      rate         = 1200
    }
  }
}

resource "auth0_guardian" "guardian" {
  email         = false
  otp           = false
  policy        = "never"
  recovery_code = false
  duo {
    enabled         = false
    hostname        = null
    integration_key = null
    secret_key      = null # sensitive
  }
  phone {
    enabled       = false
    message_types = []
    provider      = null
  }
  push {
    enabled  = false
    provider = null
  }
  webauthn_platform {
    enabled                  = false
    override_relying_party   = false
    relying_party_identifier = null
  }
  webauthn_roaming {
    enabled                  = false
    override_relying_party   = false
    relying_party_identifier = null
    user_verification        = null
  }
}
