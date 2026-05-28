output "instance_id" {
  value = aws_instance.server.id
}

output "public_ip" {
  description = "Public IP address of the EC2 instance"
  value       = aws_instance.server.public_ip
}

output "private_ip" {
  value = aws_instance.server.private_ip
}
