variable "vpc_cidr_block" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"

  validation {
    condition     = can(cidrhost(var.vpc_cidr_block, 0))
    error_message = "The VPC CIDR block must be a valid CIDR notation."
  }
}

variable "subnet_cidr_block" {
  description = "CIDR block for the Subnet"
  type        = string
  default     = "10.0.10.0/24"

  validation {
    condition     = can(cidrhost(var.subnet_cidr_block, 0))
    error_message = "The Subnet CIDR block must be a valid CIDR notation."
  }
}

variable "availability_zone" {
  description = "Availability Zone for resources"
  type        = string
}

variable "env_prefix" {
  description = "Environment prefix (e.g., dev, prod)"
  type        = string
}

variable "instance_type" {
  description = "EC2 Instance Type"
  type        = string
  default     = "t3.micro"
}

variable "public_key" {
  description = "Public key for EC2 instances"
  type        = string
  default     = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQCy+8/7x9p0q1w2e3r4t5y6u7i8o9p0a1s2d3f4g5h6j7k8l9z0x1c2v3b4n5m6L9K8J7H6G5F4D3S2A1P0O9I8U7Y6T5R4E3W2Q1M0N9B8V7C6X5Z4 user@dummy-key"
}

variable "private_key" {
  description = "Path to the private SSH key file"
  type        = string
}

variable "backend_servers" {
  description = "List of backend server configurations"
  type = list(object({
    name        = string
    script_path = string
  }))
  default = [
    {
      name        = "web-1"
      script_path = "scripts/apache-setup.sh"
    },
    {
      name        = "web-2"
      script_path = "scripts/apache-setup.sh"
    },
    {
      name        = "web-3"
      script_path = "scripts/apache-setup.sh"
    }
  ]
}
