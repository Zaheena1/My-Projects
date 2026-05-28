output "vpc_id" {
  value = aws_vpc.myapp_vpc.id
}

output "subnet_id" {
  value = aws_subnet.myapp_subnet.id
}

output "igw_id" {
  value = aws_internet_gateway.myapp_igw.id
}

output "route_table_id" {
  value = aws_route_table.myapp_route_table.id
}