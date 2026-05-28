# Networking Outputs
output "vpc_id" {
  description = "VPC ID"
  value       = module.networking.vpc_id
}

output "subnet_id" {
  description = "Subnet ID"
  value       = module.networking.subnet_id
}

# Nginx Server Outputs
output "nginx_public_ip" {
  description = "Nginx server public IP"
  value       = module.nginx_server.public_ip
}

output "nginx_instance_id" {
  description = "Nginx server instance ID"
  value       = module.nginx_server.instance_id
}

# Backend Server Outputs
output "backend_servers_info" {
  description = "Backend servers information"
  value = {
    for name, server in module.backend_servers : name => {
      instance_id = server.instance_id
      public_ip   = server.public_ip
      private_ip  = server.private_ip
    }
  }
}

# Quick Configuration Guide
output "configuration_guide" {
  value = <<-EOT
    ========================================
    DEPLOYMENT SUCCESSFUL! 
    ========================================
    Next Steps:
    1. SSH into Nginx server: ssh ec2-user@${module.nginx_server.public_ip}
    2. Edit Nginx config: sudo vim /etc/nginx/nginx.conf
    3. Update backend IPs in upstream block:
       - BACKEND_IP_1: ${module.backend_servers["web-1"].private_ip}
       - BACKEND_IP_2: ${module.backend_servers["web-2"].private_ip}
       - BACKEND_IP_3: ${module.backend_servers["web-3"].private_ip}
    4. Restart Nginx: sudo systemctl restart nginx
    5. Test: https://${module.nginx_server.public_ip}
    
    Backend Servers:
    ${join("\n    ", [for name, server in module.backend_servers : "- ${name}: ${server.public_ip} (private: ${server.private_ip})"])}
    ========================================
  EOT
}