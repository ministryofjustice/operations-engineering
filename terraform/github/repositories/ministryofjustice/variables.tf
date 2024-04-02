variable "ECR_REGION" {
  type        = string
  description = "Region of ECR repositories"
  default     = "eu-west-2"
}

variable "ECR_REGISTRY" {
  type        = string
  description = "Registry of ECR repositories"
  default     = "754256621582.dkr.ecr.eu-west-2.amazonaws.com"
}

variable "operations_engineering_team_id" {
  description = "operations-engineering team id"
  type        = string
}

variable "operations_engineering_test_team_id" {
  description = "operations-engineering-test team id"
  type        = string
}

variable "test_team_access_team_id" {
  description = "test-team-access team id"
  type        = string
}