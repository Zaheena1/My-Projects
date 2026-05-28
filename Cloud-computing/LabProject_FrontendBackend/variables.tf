variable "vpc_cidr_block" { default = "10.0.0.0/16" }
variable "subnet_cidr_block" { default = "10.0.1.0/24" }
variable "availability_zone" { default = "us-east-1a" }
variable "env_prefix" { default = "lab-project" }
variable "instance_type" { default = "t2.micro" }
variable "public_key_path" { default = "~/.ssh/id_ed25519.pub" }
variable "private_key_path" { default = "~/.ssh/id_ed25519" }
