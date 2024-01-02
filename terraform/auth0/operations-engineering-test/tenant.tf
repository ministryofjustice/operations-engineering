resource "auth0_tenant" "operations-engineering-test" {
  friendly_name         = "Operations Engineering Test"
  idle_session_lifetime = 72
  session_lifetime      = 168
  support_email         = "operations-engineering@digital.justice.gov.uk"
  support_url           = "https://github.com/ministryofjustice/operations-engineering/issues/new/choose"
}
