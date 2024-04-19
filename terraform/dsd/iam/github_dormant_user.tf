resource "aws_iam_user" "github_dormant_user" {
  name = "operations_engineering_github_dormant_user"
}
resource "aws_iam_access_key" "github_dormant_user_key" {
  user = aws_iam_user.github_dormant_user.name
}

resource "aws_s3_bucket_policy" "bucket_policy" {
  bucket = "operations-engineering-dormant-users"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:user/${aws_iam_user.github_dormant_user.name}"
        }
        Action = [
          "s3:PutObject",
          "s3:PutObjectAcl",
          "s3:PutObjectVersionAcl",
          "s3:GetObject"
        ]
        Resource = "arn:aws:s3:::operations-engineering-dormant-users/*"
      }
    ]
  })
}

data "aws_iam_access_key" "github_dormant_user_key" {
  user = aws_iam_user.github_dormant_user.name
}

resource "github_actions_secret" "aws_access_key_id" {
  repository      = "operations-engineering"
  secret_name     = "DORMANT_USER_AWS_ACCESS_KEY_ID"
  plaintext_value = data.aws_iam_access_key.github_dormant_user_key.id
}

resource "github_actions_secret" "aws_secret_access_key" {
  repository      = "operations-engineering"
  secret_name     = "DORMANT_USER_AWS_SECRET_ACCESS_KEY"
  plaintext_value = data.aws_iam_access_key.github_dormant_user_key.secret
}
