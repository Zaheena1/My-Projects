# Task: Create VPC resource
resource "aws_vpc" "myapp_vpc" {
  cidr_block           = var.vpc_cidr_block
  enable_dns_hostnames = true

  # Task: Add proper tags to all resources using env_prefix
  tags = {
    Name = "${var.env_prefix}-vpc"
  }
}

# Task: Create subnet with map_public_ip_on_launch = true
resource "aws_subnet" "myapp_subnet" {
  vpc_id                  = aws_vpc.myapp_vpc.id
  cidr_block              = var.subnet_cidr_block
  availability_zone       = var.availability_zone
  map_public_ip_on_launch = true

  # Task: Add proper tags to all resources using env_prefix
  tags = {
    Name = "${var.env_prefix}-subnet-1"
  }
}

# Task: Create and attach Internet Gateway
resource "aws_internet_gateway" "myapp_igw" {
  vpc_id = aws_vpc.myapp_vpc.id

  # Task: Add proper tags to all resources using env_prefix
  tags = {
    Name = "${var.env_prefix}-igw"
  }
}

# Task: Configure routing table (Route to IGW)
resource "aws_route_table" "myapp_route_table" {
  vpc_id = aws_vpc.myapp_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.myapp_igw.id
  }

  # Task: Add proper tags to all resources using env_prefix
  tags = {
    Name = "${var.env_prefix}-rtb"
  }
}

# Task: Associate route table with subnet
resource "aws_route_table_association" "a-rtb-subnet" {
  subnet_id      = aws_subnet.myapp_subnet.id
  route_table_id = aws_route_table.myapp_route_table.id
}