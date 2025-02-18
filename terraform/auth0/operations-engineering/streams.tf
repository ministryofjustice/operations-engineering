resource "auth0_log_stream" "eventbridge_integration" {
  name   = "EventBridge Integration"
  type   = "eventbridge"
  status = "active"

  sink {
    aws_account_id = var.streaming_aws_account_id
    aws_region     = "eu-west-2"
  }
}

import {
  to = auth0_log_stream.eventbridge_integration
  id = "lst_0000000000016742"
}
