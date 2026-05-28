# Fetch your current public IP address automatically
data "http" "my_ip" {
  url = "https://icanhazip.com"
}

locals {
  # Clean up the IP and add /32
  my_ip = "${chomp(data.http.my_ip.response_body)}/32"

  # Common tags to apply to all resources
  common_tags = {
    Environment = var.env_prefix
    Project     = "Assignment-2"
    ManagedBy   = "Terraform"
  }

  # Configuration for the 3 web servers we will build later
  backend_servers = [
    {
      name        = "web-1"
      suffix      = "1"
      script_path = "./scripts/apache-setup.sh"
    },
    {
      name        = "web-2"
      suffix      = "2"
      script_path = "./scripts/apache-setup.sh"
    },
    {
      name        = "web-3"
      suffix      = "3"
      script_path = "./scripts/apache-setup.sh"
    }
  ]
}