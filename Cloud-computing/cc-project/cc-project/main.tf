provider "aws" {
  region = var.aws_region
}

module "cdn" {
  source             = "./modules/cloudfront"
  project_name       = var.project_name
  env                = var.env
  bucket_domain_name = module.s3_site.bucket_domain_name
  comment            = "Static site for ${var.project_name}-${var.env}"
  enable_logging     = var.enable_logging
  logging_bucket     = var.logging_bucket
  tags               = local.common_tags
}

module "s3_site" {
  source         = "./modules/s3_site"
  bucket_name    = local.bucket_name
  tags           = local.common_tags
  cloudfront_arn = module.cdn.distribution_arn
}