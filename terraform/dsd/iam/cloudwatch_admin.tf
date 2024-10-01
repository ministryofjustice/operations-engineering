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

resource "aws_iam_role_policy_attachment" "cloudwatch_full_access_policy_attachment" {
  role       = aws_iam_role.cloudwatch_admin_role.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchFullAccess"
}

resource "aws_iam_role_policy_attachment" "cloudwatch_logs_full_access_policy_attachment" {
  role       = aws_iam_role.cloudwatch_admin_role.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchLogsFullAccess"
}
