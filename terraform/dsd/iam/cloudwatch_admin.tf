data "aws_iam_policy_document" "cloudwatch_admin_assume_role_policy_document" {
  version = "2012-10-17"

  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRoleWithWebIdentity"]

    principals {
      type        = "Federated"
      identifiers = [data.aws_iam_openid_connect_provider.github.arn]
    }
    condition {
      test     = "StringLike"
      variable = "${local.oidc_provider}:sub"
      values = [
        "repo:ministryofjustice/operations-engineering-github-cloudwatch-alarms:*"
      ]
    }

    condition {
      test     = "StringEquals"
      variable = "${local.oidc_provider}:aud"
      values   = ["sts.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "cloudwatch_admin_role" {
  name               = "cloudwatch_admin_role"
  assume_role_policy = data.aws_iam_policy_document.cloudwatch_admin_assume_role_policy_document.json
}

resource "aws_iam_policy" "cloudwatch_terraform_state_policy" {
  name        = "cloudwatch_terraform_state_policy"
  description = "IAM policy for CloudWatch Terraform state"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          "arn:aws:s3:::operations-engineering-test-terraform-state-bucket",
          "arn:aws:s3:::operations-engineering-test-terraform-state-bucket/terraform/dsd/cloudwatch_alarms/terraform.tfstate"
        ]
        Condition = {
          StringLike = {
            "s3:prefix" = "terraform/dsd/cloudwatch_alarms/"
          }
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "cloudwatch_terraform_state_policy_attachment" {
  role       = aws_iam_role.cloudwatch_admin_role.name
  policy_arn = aws_iam_policy.cloudwatch_terraform_state_policy.arn
}

resource "aws_iam_role_policy_attachment" "cloudwatch_full_access_policy_attachment" {
  role       = aws_iam_role.cloudwatch_admin_role.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchFullAccess"
}

resource "aws_iam_role_policy_attachment" "cloudwatch_logs_full_access_policy_attachment" {
  role       = aws_iam_role.cloudwatch_admin_role.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchLogsFullAccess"
}
