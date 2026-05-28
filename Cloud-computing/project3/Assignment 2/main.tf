terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.0"
    }
  }
}
provider "aws" {
  region = "us-east-1"
  # If you are using AWS Academy/Vocareum, make sure your credentials are set in terminal
}

module "networking" {
  source = "./modules/networking"
  # We pass the variables from our Root .tfvars into the Module
  vpc_cidr_block    = var.vpc_cidr_block
  subnet_cidr_block = var.subnet_cidr_block
  availability_zone = var.availability_zone
  env_prefix        = var.env_prefix
}
module "security" {
  source = "./modules/security"

  vpc_id     = module.networking.vpc_id
  env_prefix = var.env_prefix

  # CHANGE THIS LINE: Use local.my_ip instead of var.my_ip
  my_ip = local.my_ip
}
# --- 1. Create the Nginx Server (Load Balancer) ---
module "nginx_server" {
  source = "./modules/webserver"

  env_prefix        = var.env_prefix
  instance_name     = "nginx-proxy"
  instance_type     = var.instance_type
  availability_zone = var.availability_zone
  vpc_id            = module.networking.vpc_id
  subnet_id         = module.networking.subnet_id
  security_group_id = module.security.nginx_sg_id
  public_key = file(var.public_key)
  script_path       = "./scripts/nginx-setup.sh"
  instance_suffix   = "nginx"
  common_tags       = local.common_tags
}
# --- 2. Create the 3 Backend Servers (Web 1, 2, 3) ---
module "backend_servers" {
  # This "for_each" loop creates 3 servers automatically
  for_each = { for server in local.backend_servers : server.name => server }

  source = "./modules/webserver"

  env_prefix        = var.env_prefix
  instance_name     = each.value.name
  instance_type     = var.instance_type
  availability_zone = var.availability_zone
  vpc_id            = module.networking.vpc_id
  subnet_id         = module.networking.subnet_id
  security_group_id = module.security.backend_sg_id
  public_key = file(var.public_key)
  script_path       = each.value.script_path
  instance_suffix   = each.value.suffix
  common_tags       = local.common_tags
}