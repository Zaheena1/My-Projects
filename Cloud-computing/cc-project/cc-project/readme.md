# Multi-Environment Static Website Deployment
## AWS S3 + CloudFront with Terraform & Ansible

**Project:** Cloud Computing Project 1  
**Student:** [Your Name]  
**Environment:** Development (dev)  
**Date:** January 24, 2026

---

## 📋 Project Overview

This project demonstrates the deployment of a secure, multi-environment static website platform on AWS using Infrastructure as Code (IaC) principles. The solution uses:

- **Terraform** for infrastructure provisioning (S3 buckets, CloudFront distributions)
- **AWS CLI** for content deployment (alternative to Ansible due to Windows compatibility)
- **Modular architecture** for reusability across environments (dev, staging, prod)

### Key Features
✅ Private S3 buckets with public access blocked  
✅ CloudFront CDN for global content delivery  
✅ HTTPS enforcement (HTTP → HTTPS redirect)  
✅ Origin Access Control (OAC) for secure S3-CloudFront integration  
✅ Infrastructure as Code with Terraform modules  

---

## 🏗️ Architecture Diagram
```
┌─────────────────┐
│   End Users     │
└────────┬────────┘
         │ HTTPS
         ▼
┌─────────────────────────────────┐
│   CloudFront Distribution       │
│   (d14990poxeusqi.cloudfront.net)│
│   - HTTPS redirect               │
│   - Origin Access Control        │
└────────┬────────────────────────┘
         │ Authorized Access Only
         ▼
┌─────────────────────────────────┐
│   S3 Bucket (Private)           │
│   cc-static-shumaila-*-dev      │
│   - Block Public Access: ON     │
│   - Bucket Policy: CloudFront   │
│   - Website Files: index.html   │
└─────────────────────────────────┘

Direct Access: ❌ Blocked (403 Forbidden)
CloudFront Access: ✅ Allowed
```

---

## 📁 Project Structure
```
cc-project/
├── main.tf                    # Root module - wires everything together
├── variables.tf               # Input variables
├── outputs.tf                 # Output values
├── locals.tf                  # Local values and naming
├── terraform.tfvars           # Variable values (not committed)
├── terraform.tfvars.example   # Example configuration
├── .gitignore                 # Git ignore rules
│
├── modules/
│   ├── s3_site/              # S3 bucket module
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   │
│   └── cloudfront/           # CloudFront distribution module
│       ├── main.tf
│       ├── variables.tf
│       └── outputs.tf
│
├── ansible/
│   ├── ansible.cfg
│   ├── inventory/
│   │   └── localhost.yml
│   └── playbooks/
│       └── sync-site.yml
│
├── site/                     # Static website content
│   ├── index.html
│   └── assets/
│       └── style.css
│
├── screenshots/              # Project screenshots
└── README.md                 # This file
```

---

## 🚀 Terraform Setup & Usage

### Prerequisites
- AWS CLI configured (`aws configure`)
- Terraform installed (v1.0+)
- Git Bash or WSL (recommended for Windows)

### Deployment Steps

#### 1. Initialize Terraform
```bash
terraform init
```

#### 2. Validate Configuration
```bash
terraform validate
```

#### 3. Review Plan
```bash
terraform plan
```

#### 4. Deploy Infrastructure
```bash
terraform apply -auto-approve
```

**Note:** CloudFront distribution takes 15-20 minutes to fully deploy.

#### 5. View Outputs
```bash
terraform output
```

Expected outputs:
- `bucket_name` - S3 bucket name
- `cloudfront_domain_name` - CloudFront URL
- `website_url` - Full HTTPS website URL

---

## 📦 Content Deployment

### Using AWS CLI (Recommended for Windows)

Due to Ansible compatibility issues on Windows (Python 3.9 lacks `os.get_blocking()`), content deployment uses AWS CLI:
```bash
# Export bucket name
export BUCKET_NAME=$(terraform output -raw bucket_name)
export AWS_REGION="us-east-1"

# Sync files to S3
aws s3 sync site/ s3://$BUCKET_NAME/ --delete

# Verify upload
aws s3 ls s3://$BUCKET_NAME/ --recursive
```

### Ansible Usage (Linux/WSL)

For Linux or WSL environments, use the Ansible playbook:
```bash
cd ansible

ansible-playbook playbooks/sync-site.yml \
  --extra-vars "bucket_name=$BUCKET_NAME"
```

---

## 🧪 Testing Instructions

### 1. Access Website via CloudFront
```bash
# Get CloudFront URL
terraform output website_url

# Example: https://d14990poxeusqi.cloudfront.net
```

Open in browser - should display the website with purple gradient background.

### 2. Verify S3 Security (Should Fail)
```bash
# Get S3 direct URL
echo "https://$BUCKET_NAME.s3.amazonaws.com/index.html"
```

Open in browser - should show **Access Denied (403)** error.

### 3. Expected Results
| Access Method | Expected Result | Status |
|--------------|----------------|--------|
| CloudFront URL | Website loads | ✅ PASS |
| S3 Direct URL | Access Denied | ✅ PASS |

---

## 🧹 Cleanup Instructions

### Destroy Infrastructure

**Warning:** This will delete all resources permanently!
```bash
# Destroy all resources
terraform destroy -auto-approve

# Verify in AWS Console
# - S3: Check bucket is deleted
# - CloudFront: Check distribution is deleted
```

### Manual Cleanup (if needed)

If `terraform destroy` fails:

1. **Empty S3 bucket manually:**
```bash
   aws s3 rm s3://$BUCKET_NAME --recursive
```

2. **Then retry destroy:**
```bash
   terraform destroy -auto-approve
```

---

## 🔧 Known Issues / Troubleshooting

### Issue 1: Ansible fails on Windows
**Error:** `AttributeError: module 'os' has no attribute 'get_blocking'`

**Solution:** Use AWS CLI instead of Ansible for file synchronization:
```bash
aws s3 sync site/ s3://$BUCKET_NAME/ --delete
```

---

### Issue 2: CloudFront shows Access Denied
**Cause:** Files not uploaded or CloudFront cache not cleared

**Solution:**
1. Verify files in S3:
```bash
   aws s3 ls s3://$BUCKET_NAME/ --recursive
```
2. Wait 2-3 minutes for CloudFront cache
3. Try accessing with `?v=2` query string to bypass cache

---

### Issue 3: Bucket name already exists
**Error:** `BucketAlreadyExists: The requested bucket name is not available`

**Solution:** Change `bucket_prefix` in `terraform.tfvars`:
```hcl
bucket_prefix = "cc-static-yourname-$(date +%s)"
```

---

### Issue 4: AWS credentials expired (Learner Lab)
**Symptoms:** `InvalidClientTokenId` error

**Solution:**
1. Go to AWS Academy Learner Lab
2. Click "AWS Details" → "Show" credentials
3. Update `~/.aws/credentials` with new values
4. Retry terraform command

---

## 📊 Resources Created

| Resource Type | Count | Purpose |
|--------------|-------|---------|
| S3 Bucket | 1 | Store static website files |
| S3 Bucket Policy | 1 | Control access permissions |
| S3 Public Access Block | 1 | Prevent public access |
| CloudFront Distribution | 1 | CDN for content delivery |
| CloudFront OAC | 1 | Secure S3-CloudFront access |

**Total AWS Resources:** 5

---

## 🎓 Learning Outcomes

This project demonstrates:
- ✅ Terraform module design and reusability
- ✅ Multi-environment infrastructure patterns
- ✅ AWS S3 security best practices
- ✅ CloudFront CDN configuration
- ✅ Origin Access Control implementation
- ✅ Infrastructure as Code principles
- ✅ Problem-solving and troubleshooting

---

## 📚 References

- [Terraform AWS Provider Documentation](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [AWS S3 Documentation](https://docs.aws.amazon.com/s3/)
- [AWS CloudFront Documentation](https://docs.aws.amazon.com/cloudfront/)
- [Terraform Module Best Practices](https://www.terraform.io/docs/modules/index.html)

---

## 📝 Notes

- Environment: Development (dev)
- Region: us-east-1
- Deployment Date: January 24, 2026
- CloudFront deployment takes 15-20 minutes
- S3 bucket names must be globally unique

---

**Project Status:** ✅ Complete