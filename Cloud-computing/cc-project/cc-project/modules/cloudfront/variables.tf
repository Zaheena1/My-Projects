variable "project_name" {
  description = "Project name for CloudFront distribution"
  type        = string
}

variable "env" {
  description = "Environment name (dev, staging, prod)"
  type        = string
}

variable "bucket_domain_name" {
  description = "S3 bucket domain name for CloudFront origin"
  type        = string
}

variable "comment" {
  description = "Comment for CloudFront distribution"
  type        = string
}

variable "enable_logging" {
  description = "Enable CloudFront logging"
  type        = bool
}

variable "logging_bucket" {
  description = "S3 bucket name for CloudFront logs"
  type        = string
}

variable "tags" {
  description = "Tags for CloudFront distribution"
  type        = map(string)
}
