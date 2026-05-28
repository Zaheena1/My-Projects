variable "vpc_id" {
  description = "The ID of the VPC"
  type        = string
}

variable "env_prefix" {
  description = "Environment prefix (e.g., dev, prod)"
  type        = string
}

variable "my_ip" {
  description = "Your personal IP address for SSH access"
  type        = string
}