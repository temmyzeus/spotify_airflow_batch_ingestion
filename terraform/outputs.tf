output "Public-IP" {
  value       = aws_instance.ec2_instance.public_ip
  description = "Public IP  Adddress of our Development Environment"
}