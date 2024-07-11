resource "aws_iam_policy" "secrets_manager_policy" {
  name        = "operations_engineering_test_secrets_manager_policy"
  description = "Policy to allow access for the operations-engineering-test-secrets-manager repository to appropriate secrets in AWS Secrets Manager."
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Action = [
        "secretsmanager:GetSecretValue",
        "secretsmanager:DescribeSecret",
        "secretsmanager:GetResourcePolicy"
      ],
      Resource = "*"
    }]
  })
}

resource "aws_iam_role" "secrets_manager_role" {
  name               = "operations_engineering_test_secrets_manager_role"
  assume_role_policy = data.aws_iam_policy_document.github_actions_assume_role_policy_document.json
}

resource "aws_iam_role_policy_attachment" "secrets_manager_attachment" {
  role       = aws_iam_role.secrets_manager_role.name
  policy_arn = aws_iam_policy.secrets_manager_policy.arn
}

resource "github_actions_secret" "secrets_manager_role_arn" {
  repository      = "operations-engineering"
  secret_name     = "AWS_SECRETS_MANAGER_ROLE_ARN"
  plaintext_value = aws_iam_role.secrets_manager_role.arn
}