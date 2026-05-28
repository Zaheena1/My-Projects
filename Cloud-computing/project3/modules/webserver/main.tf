# 1. Dynamically find the latest Amazon Linux 2023 AMI
data "aws_ami" "amazon_linux_2023" {
  most_recent = true
  owners      = ["amazon"]
  filter {
    name   = "name"
    values = ["al2023-ami-2023.*-x86_64"]
  }
}

# 2. Create a unique Key Pair for this instance
resource "aws_key_pair" "ssh_key" {
  key_name   = "${var.instance_name}-${var.instance_suffix}-key"
  public_key = var.public_key
}

# 3. Create the EC2 Instance
resource "aws_instance" "server" {
  ami           = data.aws_ami.amazon_linux_2023.id
  instance_type = var.instance_type

  subnet_id              = var.subnet_id
  vpc_security_group_ids = [var.security_group_id]
  availability_zone      = var.availability_zone

  associate_public_ip_address = true
  key_name                    = aws_key_pair.ssh_key.key_name

  # Run the script file (user data)
  user_data = file(var.script_path)

  # Merge the common tags with the specific Name tag
  tags = merge(
    var.common_tags,
    {
      Name = "${var.instance_name}-${var.instance_suffix}"
    }
  )
}