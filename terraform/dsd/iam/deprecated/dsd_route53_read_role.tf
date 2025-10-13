resource "aws_iam_role" "dsd_route53_read_role" {
  name               = "dsd_route53_read_role"
  assume_role_policy = data.aws_iam_policy_document.github_actions_assume_role_policy_document.json
}

data "aws_iam_policy" "dsd_route53_read_role_policy" {
  arn = "arn:aws:iam::aws:policy/AmazonRoute53ReadOnlyAccess"
}

resource "aws_iam_role_policy_attachment" "dsd_route53_read_role_policy_attatchment" {
  role       = aws_iam_role.dsd_route53_read_role.name
  policy_arn = data.aws_iam_policy.dsd_route53_read_role_policy.arn
}

resource "github_actions_secret" "dsd_route53_read_role_arn" {
  repository      = "operations-engineering"
  secret_name     = "DSD_ROUTE53_READ_ROLE_ARN"
  plaintext_value = aws_iam_role.dsd_route53_read_role.arn
}
