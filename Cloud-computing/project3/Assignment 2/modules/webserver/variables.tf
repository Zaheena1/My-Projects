variable "env_prefix" {}
variable "instance_name" {}
variable "instance_type" {}
variable "availability_zone" {}
variable "vpc_id" {}
variable "subnet_id" {}
variable "security_group_id" {}
variable "public_key" {}
variable "script_path" {}
variable "instance_suffix" {}

variable "common_tags" {
  type = map(string)
}