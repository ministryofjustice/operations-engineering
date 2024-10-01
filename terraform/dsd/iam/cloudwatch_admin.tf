resource "aws_iam_role" "cloudwatch_admin_role" {
  name               = "cloudwatch_admin_role"
  assume_role_policy = data.aws_iam_policy_document.github_actions_assume_role_policy_document.json
}

resource "aws_iam_role_policy_attachment" "cloudwatch_full_access_policy_attachment" {
  role       = aws_iam_role.cloudwatch_admin_role.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchFullAccess"
}

resource "aws_iam_role_policy_attachment" "cloudwatch_logs_full_access_policy_attachment" {
  role       = aws_iam_role.cloudwatch_admin_role.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchLogsFullAccess"
}
