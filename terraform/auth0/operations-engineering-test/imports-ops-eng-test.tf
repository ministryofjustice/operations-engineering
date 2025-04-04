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
