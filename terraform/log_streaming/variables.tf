variable "github_auditlog_s3bucket" {
  type        = string
  description = "Source S3 bucket of GitHub Audit Log, enter existing or specify new bucket name"
  default     = "test-github-enterprise-audit"
}

variable "create_github_auditlog_s3bucket" {
  type        = bool
  description = "If `true` the module will create the bucket github_auditlog_s3bucket."
  default     = false
}

variable "cloudtrail_lake_channel_arn" {
  type        = string
  description = "channel ARN that you setup from CloudTrail Lake integration for GitHub Audit Log"
  default     = "arn:aws:cloudtrail:eu-west-2:880656497252:channel/408043b5-2c04-438e-93d0-76e02ba38582"
}

variable "github_audit_allow_list" {
  type        = string
  description = "Comma delimited list of GitHub Audit Event to be allowed for ingestion to CloudTrail Open Audit"
  default     = ".*"
}
