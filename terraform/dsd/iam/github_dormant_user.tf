resource "aws_iam_policy" "github_dormant_user_policy" {
  name        = "DormantUserS3Access"
  description = "Policy to grant S3 access to the GitHub Dormant User role"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action   = ["s3:PutObject", "s3:GetObject", "s3:DeleteObject"],
        Effect   = "Allow",
        Resource = "arn:aws:s3:::operations-engineering-dormant-users/*"
      },
    ]
  })
}

resource "aws_iam_role" "github_dormant_user_role" {
  name = "github_dormant_user_role"

  assume_role_policy = data.aws_iam_policy_document.github_actions_assume_role_policy_document.json
}

resource "aws_iam_role_policy_attachment" "role_policy_attachment" {
  role       = aws_iam_role.github_dormant_user_role.name
  policy_arn = aws_iam_policy.github_dormant_user_policy.arn
}

resource "github_actions_secret" "aws_role_arn" {
  repository      = "operations-engineering"
  secret_name     = "GH_DORMANT_USER_AWS_ROLE_ARN"
  plaintext_value = aws_iam_role.github_dormant_user_role.arn
}
