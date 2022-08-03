variable "bucket_prefix" {
  type        = string
  description = "Prefix name of S3 Bucket"
}

variable "profile" {
  type        = string
  default     = "default"
  description = "AWS Profile"
}

variable "region" {
  type        = string
  default     = "us-west-2"
  description = "AWS Resource Region"
}

variable "aws_config_path" {
  type        = tuple([string])
  default     = ["$HOME/.aws/config"]
  description = "AWS Configuration Path"
}

variable "aws_credentials_path" {
  type        = tuple([string])
  default     = ["$HOME/.aws/credentials"]
  description = "AWS Credentials Path"
}

variable "AIRFLOW_TAG" {
  type        = map(any)
  description = "Tag for Resources used by Airflow"
  default = {
    Name = "Airflow_Instance"
    App  = "Airflow"
  }
}

variable "AZ" {
  type        = string
  description = "Availability Zone(s)"
}

variable "public_key_path" {
  type        = string
  description = "Path to public key"
}
