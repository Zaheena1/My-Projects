variable "aws_region" {
  description = "AWS region"
  type        = string
}

variable "project_name" {
  description = "Project name"
  type        = string
}

variable "env" {
  description = "Environment name"
  type        = string
}

variable "bucket_prefix" {
  description = "Prefix for S3 bucket name"
  type        = string
}

variable "enable_logging" {
  description = "Enable CloudFront logging"
  type        = bool
}

variable "logging_bucket" {
  description = "S3 bucket for CloudFront logs"
  type        = string
}
variable "tags" {
  description = "Common tags"
  type        = map(string)
}
