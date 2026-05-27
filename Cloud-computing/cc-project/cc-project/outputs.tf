output "bucket_name" {
  description = "S3 bucket name for static site"
  value       = module.s3_site.bucket_name
}

output "bucket_arn" {
  description = "S3 bucket ARN"
  value       = module.s3_site.bucket_arn
}

output "cloudfront_domain_name" {
  description = "CloudFront distribution domain name"
  value       = module.cdn.domain_name
}

output "cloudfront_distribution_id" {
  description = "CloudFront distribution ID"
  value       = module.cdn.distribution_id
}

output "website_url" {
  description = "Full website URL"
  value       = "https://${module.cdn.domain_name}"
}