resource "aws_iam_policy" "dns_check_change_status_policy" {
  name        = "DnsCheckChangeStatusPolicy"
  description = "Policy to enable DNS Check Change Status"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "route53:ListHostedZones",
          "route53:ListHostedZonesByName",
          "route53:ListResourceRecordSets",
          "cloudtrail:LookupEvents"
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role" "dns_check_change_status_user_role" {
  name = "dns_check_change_status_user_role"

  assume_role_policy = data.aws_iam_policy_document.github_actions_assume_role_policy_document.json
}

resource "aws_iam_role_policy_attachment" "dns_check_change_status_role_policy_attachment" {
  role       = aws_iam_role.dns_check_change_status_user_role.name
  policy_arn = aws_iam_policy.dns_check_change_status_policy.arn
}

resource "github_actions_secret" "dns_check_change_status_aws_role_arn" {
  repository      = "dns"
  secret_name     = "DNS_CHECK_CHANGE_STATUS_AWS_ROLE_ARN"
  plaintext_value = aws_iam_role.dns_check_change_status_user_role.arn
}
