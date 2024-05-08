
resource "aws_iam_policy" "dns_change_records_policy" {
  name        = "Route53ChangeRecordsPolicy"
  description = "A policy that allows modification of the Route53 record sets for the dns-test.service.justice.gov.uk hosted zone."

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "route53:ChangeResourceRecordSets",
        "route53:ListResourceRecordSets"
      ],
      "Resource": "arn:aws:route53:::hostedzone/test-dns.service.justice.gov.uk"
    },
    {
      "Effect": "Allow",
      "Action": [
        "route53:GetHostedZone",
        "route53:ListHostedZones"
      ],
      "Resource": "*"
    }
  ]
}
EOF
}

resource "aws_iam_role" "octodns_role" {
  name = "octodns_role"

  assume_role_policy = data.aws_iam_policy_document.github_actions_assume_role_policy_document.json
}

resource "aws_iam_role_policy_attachment" "octo_dns_role_policy_attachment" {
  role       = aws_iam_role.octodns_role.name
  policy_arn = aws_iam_policy.dns_change_records_policy.arn
}

resource "github_actions_secret" "octodns_role" {
  repository      = "operations-engineering-dns-spike"
  secret_name     = "OCTODNS_AWS_ROLE_ARN"
  plaintext_value = aws_iam_role.octodns_role.arn
}
