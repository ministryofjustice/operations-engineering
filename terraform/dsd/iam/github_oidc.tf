locals {
  oidc_provider = "token.actions.githubusercontent.com"
}

data "aws_iam_openid_connect_provider" "github" {
  url = "https://${local.oidc_provider}"
}

data "aws_iam_policy_document" "github_actions_assume_role_policy_document" {
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
        "repo:ministryofjustice/operations-engineering:*",
        "repo:ministryofjustice/dns:*"
      ]
    }

    condition {
      test     = "StringEquals"
      variable = "${local.oidc_provider}:aud"
      values   = ["sts.amazonaws.com"]
    }
  }
}
