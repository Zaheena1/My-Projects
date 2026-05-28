#!/bin/bash
set -e

# --- 1. Install Nginx and OpenSSL ---
yum update -y
yum install -y nginx openssl
systemctl start nginx
systemctl enable nginx

# --- 2. Create SSL Certificates (HTTPS) ---
mkdir -p /etc/ssl/private
mkdir -p /etc/ssl/certs

# Get the Public IP so the certificate matches the server
TOKEN=$(curl -s -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")
PUBLIC_IP=$(curl -s -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/public-ipv4)

# Generate the self-signed certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/ssl/private/selfsigned.key \
  -out /etc/ssl/certs/selfsigned.crt \
  -subj "/CN=$PUBLIC_IP" \
  -addext "subjectAltName=IP:$PUBLIC_IP" \
  -addext "basicConstraints=CA:FALSE" \
  -addext "keyUsage=digitalSignature,keyEncipherment" \
  -addext "extendedKeyUsage=serverAuth"

echo "Self-signed certificate created for IP: $PUBLIC_IP"

# --- 3. Configure Nginx ---
# Backup the old config first
cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.bak

# Write the new configuration
cat > /etc/nginx/nginx.conf <<'EOF'
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log notice;
pid /run/nginx.pid;
events {
    worker_connections 1024;
}
http {
    # Logging Settings
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for" '
                    'Cache: $upstream_cache_status';
    access_log /var/log/nginx/access.log main;

    # Basic Settings
    sendfile on;
    tcp_nopush on;
    keepalive_timeout 65;
    types_hash_max_size 4096;
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Compression
    gzip on;
    gzip_vary on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml;

    # Caching Setup
    proxy_cache_path /var/cache/nginx
                      levels=1:2
                      keys_zone=my_cache:10m
                      max_size=1g
                      inactive=60m
                      use_temp_path=off;

    # --- UPSTREAM SERVERS (The Load Balancer Logic) ---
    # IMPORTANT: You must update these IPs manually after Terraform deploys!
    upstream backend_servers {
        # Primary servers
        server 10.0.10.210:80;  # Web-1
        server 10.0.10.153:80;  # Web-2
        
        # Backup server (only used if others fail)
        server 10.0.10.121:80 backup; # Web-3
    }

    # --- HTTPS Server (Port 443) ---
    server {
        listen 443 ssl http2;
        server_name _;

        # SSL Keys
        ssl_certificate /etc/ssl/certs/selfsigned.crt;
        ssl_certificate_key /etc/ssl/private/selfsigned.key;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_prefer_server_ciphers on;

        # Security Headers
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;

        # Proxy Rules
        location / {
            proxy_pass http://backend_servers;
            
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            # Enable Caching
            proxy_cache my_cache;
            proxy_cache_valid 200 60m;
            proxy_cache_valid 404 10m;
            proxy_cache_bypass $http_cache_control;
            add_header X-Cache-Status $upstream_cache_status;
        }

        # Health Check
        location /health {
            access_log off;
            return 200 "Nginx is healthy\n";
            add_header Content-Type text/plain;
        }
    }

    # --- HTTP Server (Redirect to HTTPS) ---
    server {
        listen 80;
        server_name _;
        
        location / {
            return 301 https://$host$request_uri;
        }

        location /health {
            access_log off;
            return 200 "Nginx is healthy\n";
            add_header Content-Type text/plain;
        }
    }
}
EOF

# --- 4. Final Steps ---
mkdir -p /var/cache/nginx
chown -R nginx:nginx /var/cache/nginx

# Restart Nginx to apply changes
nginx -t && systemctl restart nginx
echo "Nginx setup completed successfully!"