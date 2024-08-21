resource "null_resource" "build_lambdas" {
  provisioner "local-exec" {
    command = "cd .terraform/modules/github-cloudtrail-auditlog && make all"
  }

  triggers = {
    always_run = "${timestamp()}"
  }
}

module "github-cloudtrail-auditlog" {
  source                          = "github.com/ministryofjustice/operations-engineering-cloudtrail-lake-github-audit-log-terraform-module?ref=main"
  create_github_auditlog_s3bucket = var.create_github_auditlog_s3bucket
  github_auditlog_s3bucket        = var.github_auditlog_s3bucket
  cloudtrail_lake_channel_arn     = var.cloudtrail_lake_channel_arn
  github_audit_allow_list         = var.github_audit_allow_list
}
