resource "aws_iam_user" "octodns_user" {
  name = "octodns-cicd-user"
}

resource "aws_iam_policy" "octodns_policy" {
  name        = "OctoDNSPolicy"
  description = "Policy for OctoDNS to manage Route53"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "route53:ChangeResourceRecordSets",
          "route53:CreateHostedZone",
          "route53:ListHealthChecks",
          "route53:ListHostedZones",
          "route53:ListHostedZonesByName",
          "route53:ListResourceRecordSets"
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_user_policy_attachment" "octodns_user_policy_attachment" {
  user       = aws_iam_user.octodns_user.name
  policy_arn = aws_iam_policy.octodns_policy.arn
}

resource "aws_iam_access_key" "octodns_access_key" {
  user = aws_iam_user.octodns_user.name
}

resource "github_actions_secret" "octodns_aws_access_key_id" {
  repository      = "dns"
  secret_name     = "OCTODNS_AWS_ACCESS_KEY_ID"
  plaintext_value = aws_iam_access_key.octodns_access_key.id
}

resource "github_actions_secret" "octodns_aws_secret_access_key" {
  repository      = "dns"
  secret_name     = "OCTODNS_AWS_SECRET_ACCESS_KEY"
  plaintext_value = aws_iam_access_key.octodns_access_key.secret
}
