terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

# --- Networking ---
resource "aws_vpc" "main" {
  cidr_block = var.vpc_cidr_block
  tags = { Name = "${var.env_prefix}-vpc" }
}

module "subnet" {
  source = "./modules/subnet"
  vpc_id            = aws_vpc.main.id
  subnet_cidr_block = var.subnet_cidr_block
  availability_zone = var.availability_zone
  env_prefix        = var.env_prefix
}

resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.main.id
  tags = { Name = "${var.env_prefix}-igw" }
}

resource "aws_route_table" "public_rt" {
  vpc_id = aws_vpc.main.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }
  tags = { Name = "${var.env_prefix}-rt" }
}

resource "aws_route_table_association" "public_rt_assoc" {
  subnet_id      = module.subnet.subnet_id
  route_table_id = aws_route_table.public_rt.id
}

# --- Security Group ---
data "http" "my_ip" {
  url = "https://icanhazip.com"
}

resource "aws_security_group" "web_sg" {
  name   = "${var.env_prefix}-sg"
  vpc_id = aws_vpc.main.id

  # SSH from YOUR IP only
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["${chomp(data.http.my_ip.response_body)}/32"]
  }

  # HTTP from Anywhere
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Allow internal communication
  ingress {
    from_port = 0
    to_port   = 0
    protocol  = "-1"
    self      = true
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# --- Instances ---
data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]
  filter {
    name   = "name"
    values = ["al2023-ami-2023.*-x86_64"]
  }
}

resource "aws_key_pair" "ssh_key" {
  key_name   = "${var.env_prefix}-key"
  public_key = file(var.public_key_path)
}

resource "aws_instance" "frontend" {
  ami                    = data.aws_ami.amazon_linux.id
  instance_type          = var.instance_type
  subnet_id              = module.subnet.subnet_id
  vpc_security_group_ids = [aws_security_group.web_sg.id]
  key_name               = aws_key_pair.ssh_key.key_name
  tags = { Name = "${var.env_prefix}-frontend" }
}

resource "aws_instance" "backend" {
  count                  = 3
  ami                    = data.aws_ami.amazon_linux.id
  instance_type          = var.instance_type
  subnet_id              = module.subnet.subnet_id
  vpc_security_group_ids = [aws_security_group.web_sg.id]
  key_name               = aws_key_pair.ssh_key.key_name
  tags = { Name = "${var.env_prefix}-backend-${count.index + 1}" }
}

# --- Automation ---
resource "local_file" "ansible_inventory" {
  content = templatefile("${path.module}/ansible/inventory.tftpl", {
    frontend_ip = aws_instance.frontend.public_ip
    backend_ips = aws_instance.backend[*].public_ip
    private_key = var.private_key_path
  })
  filename = "${path.module}/ansible/inventory/hosts"
}

resource "null_resource" "ansible_trigger" {
  triggers = {
    frontend_id = aws_instance.frontend.id
    backend_ids = join(",", aws_instance.backend[*].id)
  }

  depends_on = [
    local_file.ansible_inventory,
    aws_instance.frontend,
    aws_instance.backend
  ]

  provisioner "local-exec" {
    command = <<EOT
      echo "Waiting 45s for instances to initialize..."
      sleep 45
      cd ansible
      ansible-playbook -i inventory/hosts playbooks/site.yaml
    EOT
  }
}
