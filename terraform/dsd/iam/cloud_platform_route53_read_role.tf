resource "aws_iam_role" "assume_cloud_platform_route53_read_role" {
  name               = "assume_cloud_platform_route53_read_role"
  assume_role_policy = data.aws_iam_policy_document.github_actions_assume_role_policy_document.json
}

resource "github_actions_secret" "assume_cloud_platform_route53_read_role_arn" {
  repository      = "operations-engineering"
  secret_name     = "ASSUME_CLOUD_PLATFORM_ROUTE53_READ_ROLE_ARN"
  plaintext_value = aws_iam_role.assume_cloud_platform_route53_read_role.arn
}
