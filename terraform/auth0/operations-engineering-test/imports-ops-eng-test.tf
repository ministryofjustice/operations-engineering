import {
  to = auth0_client.terraform_provider_auth0
  id = "xI46sB1af7TKeycQ3xfTA2qIxeLiX2R8"
}

import {
  to = auth0_client.github
  id = "Ez0SbR2tPwaDgL6tjWALIKSy4m3WtSFr"
}

import {
  to = auth0_client.default_app
  id = "qkvVnu0b4pXd6FdEbjm073w4MchhpOoB"
}

import {
  to = auth0_connection.google_workspace
  id = "con_VacE1q5yZxznHQAj"
}

# This resource can be imported by specifying the
# connection ID and client ID separated by "::" (note the double colon)
# <connectionID>::<clientID>

import {
  to = auth0_connection_client.google_workspace_github
  id = "con_VacE1q5yZxznHQAj::Ez0SbR2tPwaDgL6tjWALIKSy4m3WtSFr"
}
import {
  to = auth0_connection.google_oauth2
  id = "con_yyrB18AQbSUcMLTm"
}

# As this is not a resource identifiable by an ID within the Auth0 Management API,
# tenant can be imported using a random string.
#
# We recommend [Version 4 UUID](https://www.uuidgenerator.net/version4)
import {
  to = auth0_tenant.tenant
  id = "db796dd0-9670-4641-85bb-b6462e3ab6a9"
}

import {
  to = auth0_resource_server.auth0_management_api
  id = ""
}

# Use random string!
# We recommend [Version 4 UUID](https://www.uuidgenerator.net/version4)

import {
  to = auth0_attack_protection.attack_protection
  id = "f9e2376d-c64d-44ec-9a34-04b65dabb0ca"
}
