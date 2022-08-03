output "Instance-Name-Output" {
  description = "Name of EC2 instance created for Airflow"
  value       = aws_instance.airflow_instance
}