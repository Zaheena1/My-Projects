locals {
  # Standardized tags to be used across all resources
  common_tags = {
    Project     = "CloudComputing-Lab"
    Environment = var.env_prefix
    ManagedBy   = "Terraform"
    Owner       = "Urooj"
  }
}
