# Troubleshooting Guide – Assignment 2

This document lists common issues encountered during deployment and testing, 
along with their solutions.

---

## 1. SSH Connection Timeout

### Issue
Unable to connect to EC2 instances via SSH.

### Possible Causes
- Incorrect security group rules
- Wrong key pair used
- Instance not in running state

### Solution
- Ensure port 22 is open in the security group
- Verify correct `.pem` key is used
- Confirm instance is running in AWS Console

---

## 2. Backend Servers Not Responding

### Issue
Nginx shows 502 Bad Gateway errors.

### Possible Causes
- Apache service not running
- Incorrect backend IP addresses
- Firewall blocking traffic

### Solution
- Restart Apache:
sudo systemctl restart httpd

- Verify backend IPs in Nginx config
- Check backend security group rules

---

## 3. Load Balancing Not Working

### Issue
Requests always go to the same backend server.

### Possible Causes
- Browser caching
- Incorrect Nginx configuration

### Solution
- Clear browser cache
- Reload Nginx configuration:
sudo nginx -t
sudo systemctl reload nginx

---

## 4. Cache Headers Not Appearing

### Issue
`X-Cache-Status` header not visible.

### Possible Causes
- Cache not configured correctly
- Browser cache interfering

### Solution
- Verify Nginx cache configuration
- Clear browser cache
- Restart Nginx service

---

## 5. Terraform Apply Errors

### Issue
Terraform fails during `apply`.

### Possible Causes
- Missing variables
- Invalid AWS credentials
- Incorrect region

### Solution
- Check `terraform.tfvars`
- Verify AWS credentials:
aws configure

- Run:
terraform validate

---

## 6. Cleanup Issues

### Issue
Resources not destroyed after `terraform destroy`.

### Solution
- Re-run:
terraform destroy

- Verify AWS Console for remaining resources
- Check `terraform.tfstate` is empty

---

## 7. Log Locations

- Nginx logs: `/var/log/nginx/`
- Apache logs: `/var/log/httpd/`
- System logs: `/var/log/messages`
