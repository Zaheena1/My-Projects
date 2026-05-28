<!-- ========================= -->
<!-- Assignment 2 - Multi-Tier Web Infrastructure 
<!-- ========================= -->

#  Project overview
This project implements a high-availability multi-tier web infrastructure on AWS using Terraform.
It features an Nginx server acting as a secure Reverse Proxy and Load Balancer, distributing traffic to three Apache (httpd) backend servers.

The infrastructure is hardened with SSL/TLS, specialized Security Headers, Rate Limiting, and automated Health Checks.

---

## Architecture Diagram

```
┌───────────────────────────────────────────┐
│                 Internet                  │
└─────────────────┬─────────────────────────┘
                  │
                  │ HTTPS (443)
                  │ HTTP (80)
                  ▼
            ┌─────────────────────┐
            │    Nginx Server     │
            │   (Load Balancer)   │
            │   - SSL/TLS         │
            │   - Caching         │
            │   - Reverse Proxy   │
            └─────────┬───────────┘
                      │ 
          ┌───────────┼───────────┐
          │           │           │
          ▼           ▼           ▼
        ┌─────┐     ┌─────┐     ┌─────┐
        │Web-1│     │Web-2│     │Web-3│
        │     │     │     │     │Backup
        └─────┘     └─────┘     └─────┘
```

---

## Components Description

### Nginx Server (Load Balancer)

Role: Entry point for all traffic, handles SSL termination, and reverse proxy.
**Instance ID**: i-013c6f66f5b6b7ec7  
**Public IP**: 98.92.144.147  
**Security Group ID**: sg-070840d451830abf9 (prod-nginx-sg)

---

### Web Servers (Backend Tier)
<!-- Backend application servers -->

**Web-1**: i-06e232a8944a458ce | Public IP: 34.206.3.224 | Private IP: 10.0.10.210  
**Web-2**: i-04921265ac0e79fe2 | Public IP: 3.224.135.171 | Private IP: 10.0.10.153  
**Web-3** (Backup): i-0dab6b26a2f4d6349 | Public IP: 44.204.142.153 | Private IP: 10.0.10.121  
**Backend Security Group ID**: sg-0d728b25b03b3d3c9 (prod-backend-sg)

---

## Infrastructure Details
<!-- AWS networking details -->

VPC ID: vpc-0488d8748ab09af61 (prod-vpc)  
Subnet ID: subnet-0ff5c2bbac0736ba7 (prod-subnet-1)

---

## Prerequisites
<!-- Tools and requirements -->

**Tools Required**:Terraform, AWS CLI, SSH client.  

**AWS Setup**
Configure credentials via `aws configure` with correct IAM permissions. 

**SSH Key** 
Ensure the private key used during deployment is available for server access.

---

## Deployment Instructions

### Update Variables as per Your AWS setup
<!-- Terraform variables -->

Ensure your `terraform.tfvars` reflects the following:

```
vpc_id = "vpc-0488d8748ab09af61"
subnet_id = "subnet-0ff5c2bbac0736ba7"
```

### Initialize Terraform
<!-- Initialize terraform working directory -->

```
terraform init
```

### Apply Configuration
<!-- Deploy infrastructure -->

terraform apply -auto-approve

---

## Configuration Guide (Parts 1-5)

### SSL & Security Hardening
<!-- Security configurations -->

**SSL Termination**: Configured on Port 443 using self-signed certificates.  

**Security Headers**: Added HSTS, X-Frame-Options, and X-Content-Type-Options to Nginx.  

**HTTP Redirect**: Implemented 301 redirect from Port 80 to 443.

---

## Updating Backend IPs in Nginx

### Edit Nginx Configuration
<!-- SSH and configuration update -->

SSH into Nginx:

```
ssh ec2-user@98.92.144.147
```
Update the upstream block in `/etc/nginx/nginx.conf`:
```
upstream backend {
    server 10.0.10.210; # Web-1
    server 10.0.10.153; # Web-2
    server 10.0.10.121 backup; # Web-3 (Backup)
}
```

Restart Nginx:

```
sudo systemctl restart nginx
```


## Bonus Features
<!-- Extra enhancements -->

**Bonus 1**: Custom 404 and 502/503 error pages.  
**Bonus 2**: Rate limiting set to 10r/s with a burst of 20.  
**Bonus 3**: Health check shell script monitoring backend connectivity.

---

## Testing Procedures
<!-- Validation and checks -->

- Verify HTTPS access via Nginx public IP  
- Stop one backend to test failover  
- Check rate limiting behavior  
- Validate custom error pages  

---

## Troubleshooting

### Log Locations
<!-- Log files -->

Nginx Access Log: /var/log/nginx/access.log  
Nginx Error Log: /var/log/nginx/error.log  
Health Log: /home/ec2-user/health_check.log

---

### Debug Commands
<!-- Debugging utilities -->

Check Syntax:
```
sudo nginx -t
```
Service Status:
```
sudo systemctl status nginx
```
