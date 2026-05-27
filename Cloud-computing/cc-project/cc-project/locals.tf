locals {
  common_tags = merge(
    {
      Project     = var.project_name
      Environment = var.env
      ManagedBy   = "Terraform"
    },
    var.tags
  )

  bucket_name = lower("${var.bucket_prefix}-${var.project_name}-${var.env}")
}
