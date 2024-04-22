resource "aws_iam_user" "github_dormant_user" {
  name = "operations_engineering_github_dormant_user"
}

resource "aws_iam_policy" "user_policy" {
  name        = "DormantUserS3Access"
  description = "Policy to grant S3 access to github_dormant_user"

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

resource "aws_iam_user_policy_attachment" "user_policy_attachment" {
  user       = aws_iam_user.github_dormant_user.name
  policy_arn = aws_iam_policy.user_policy.arn
}

resource "aws_iam_access_key" "user_key" {
  user = aws_iam_user.github_dormant_user.name
}

resource "github_actions_secret" "aws_access_key_id" {
  repository      = "operations-engineering"
  secret_name     = "AWS_ACCESS_KEY_ID"
  plaintext_value = aws_iam_access_key.user_key.id
}

resource "github_actions_secret" "aws_secret_access_key" {
  repository      = "operations-engineering"
  secret_name     = "AWS_SECRET_ACCESS_KEY"
  plaintext_value = aws_iam_access_key.user_key.secret
}
