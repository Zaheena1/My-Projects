# Troubleshooting Guide

## Common Issues and Solutions

### 1. Ansible Installation Issues on Windows

**Problem:** `AttributeError: module 'os' has no attribute 'get_blocking'`

**Cause:** Python 3.9 on Windows lacks required OS functions

**Solution:** Use AWS CLI instead:
```bash
aws s3 sync site/ s3://$BUCKET_NAME/ --delete
```

---

### 2. Bucket Already Exists

**Problem:** `BucketAlreadyExists: The requested bucket name is not available`

**Solution:** Change bucket_prefix to make it unique:
```hcl
bucket_prefix = "cc-static-yourname-20260124"
```

---

### 3. CloudFront Access Denied

**Problem:** CloudFront shows Access Denied after deployment

**Possible Causes:**
- Files not uploaded to S3
- CloudFront still deploying
- Bucket policy misconfigured

**Solutions:**
1. Verify files in S3: `aws s3 ls s3://$BUCKET_NAME/ --recursive`
2. Wait 5-10 minutes for CloudFront deployment
3. Check bucket policy allows CloudFront service principal

---

### 4. Terraform Destroy Fails

**Problem:** `BucketNotEmpty: The bucket you tried to delete is not empty`

**Solution:**
```bash
aws s3 rm s3://$BUCKET_NAME --recursive
terraform destroy -auto-approve
```

---

### 5. AWS Credentials Expired (Learner Lab)

**Problem:** `InvalidClientTokenId: The security token included in the request is invalid`

**Solution:**
1. Start AWS Learner Lab
2. Click AWS Details → Show credentials
3. Update ~/.aws/credentials
4. Retry command