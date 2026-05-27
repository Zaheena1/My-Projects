# Architecture Documentation

## System Architecture

This project implements a secure static website hosting solution using:

### Components
1. **S3 Bucket** - Private storage for static files
2. **CloudFront Distribution** - CDN for global content delivery
3. **Origin Access Control** - Secure S3-CloudFront integration

### Data Flow
1. User requests website via CloudFront URL
2. CloudFront checks cache
3. If not cached, CloudFront requests from S3 using OAC
4. S3 verifies CloudFront authorization
5. Content delivered to user via HTTPS

### Security Features
- S3 bucket fully private (all public access blocked)
- CloudFront uses Origin Access Control (OAC)
- HTTPS enforced (HTTP → HTTPS redirect)
- Bucket policy allows only CloudFront service principal

## Infrastructure as Code

All resources managed via Terraform modules for:
- Consistency across environments
- Reusability (dev, staging, prod)
- Version control
- Easy teardown/recreation