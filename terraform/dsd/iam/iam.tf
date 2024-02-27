locals {
  oidc_provider = "token.actions.githubusercontent.com"
}

data "aws_iam_openid_connect_provider" "github" {
  url = "https://${local.oidc_provider}"
}

resource "aws_iam_role" "r53_backup_role" {
  name               = "operations-engineering-r53-backup-role"
  assume_role_policy = data.aws_iam_policy_document.assume_role_policy_document.json
}

data "aws_iam_policy_document" "assume_role_policy_document" {
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
      values   = ["repo:ministryofjustice/operations-engineering:*"]
    }

    condition {
      test     = "StringEquals"
      variable = "${local.oidc_provider}:aud"
      values   = ["sts.amazonaws.com"]
    }
  }
}

data "aws_iam_policy_document" "r53_read_policy_document" {
  version = "2012-10-17"

  statement {
    effect = "Allow"
    actions = [
      "route53:UpdateHostedZoneComment",
      "route53:Get*",
      "route53:List*"
    ]
    resources = ["*"]
  }
}

resource "aws_iam_policy" "r53_read_policy" {
  name   = "r53_read_policy"
  policy = data.aws_iam_policy_document.r53_read_policy_document.json
}

resource "aws_iam_role_policy_attachment" "r53_read_policy_attachment" {
  role       = aws_iam_role.r53-backup-role.name
  policy_arn = aws_iam_policy.r53_read_policy.arn
}

resource "github_actions_secret" "role_arn" {
  repository      = "operations-engineering"
  secret_name     = "AWS_DSD_R53_EXPORT_ROLE_ARN"
  plaintext_value = aws_iam_role.r53-backup-role.arn
}
