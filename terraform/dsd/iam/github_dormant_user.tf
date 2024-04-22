resource "aws_iam_user" "github_dormant_user" {
  name = "operations_engineering_github_dormant_user"
}

resource "aws_iam_policy" "github_dormant_user_policy" {
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

# This block creates an IAM role named `github_dormant_user_role`.
# The `assume_role_policy` is set to allow EC2 instances to assume this role.
# This is specified by the `Service = "ec2.amazonaws.com"` line in the `Principal` block.
# If a different AWS service or entity needs to assume the role, this value should be replaced with the appropriate service principal.
resource "aws_iam_role" "github_dormant_user_role" {
  name = "github_dormant_user_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = "sts:AssumeRole",
        Principal = {
          Service = "ec2.amazonaws.com"
        },
        Effect = "Allow",
      },
    ]
  })
}

resource "aws_iam_role_policy_attachment" "role_policy_attachment" {
  role       = aws_iam_role.github_dormant_user_role.name
  policy_arn = aws_iam_policy.github_dormant_user_policy.arn
}

resource "github_actions_secret" "aws_role_arn" {
  repository      = "operations-engineering"
  secret_name     = "GITHUB_DORMANT_USER_AWS_ROLE_ARN"
  plaintext_value = aws_iam_role.github_dormant_user_role.arn
}
resource "aws_iam_user_policy_attachment" "user_policy_attachment" {
  user       = aws_iam_user.github_dormant_user.name
  policy_arn = aws_iam_policy.github_dormant_user_policy.arn
}
