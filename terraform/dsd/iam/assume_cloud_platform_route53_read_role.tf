resource "aws_iam_role" "assume_cloud_platform_route53_read_role" {
  name               = "assume_cloud_platform_route53_read_role"
  assume_role_policy = data.aws_iam_policy_document.github_actions_assume_role_policy_document.json
}

resource "aws_iam_policy" "assume_cloud_platform_route53_read_role_policy" {
  name        = "AssumeCloudPlatformRoute53ReadRolePolicy"
  description = "A policy that allows a user to assume the Cloud Platforms Route53 Read role"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action   = "sts:AssumeRole",
        Effect   = "Allow",
        Resource = "arn:aws:iam::${var.cloud_platform_account_id}:role/ops-eng-route53-readonly"
      },
    ]
  })
}

resource "aws_iam_role_policy_attachment" "assume_cloud_platform_route53_read_role_policy_attatchment" {
  role       = aws_iam_role.assume_cloud_platform_route53_read_role.name
  policy_arn = aws_iam_policy.assume_cloud_platform_route53_read_role_policy.arn
}

resource "github_actions_secret" "assume_cloud_platform_route53_read_role_arn" {
  repository      = "operations-engineering"
  secret_name     = "ASSUME_CLOUD_PLATFORM_ROUTE53_READ_ROLE_ARN"
  plaintext_value = aws_iam_role.assume_cloud_platform_route53_read_role.arn
}
