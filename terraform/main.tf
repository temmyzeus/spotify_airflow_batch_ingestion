terraform {
  required_version = ">= 0.12"
  backend "local" {}
  required_providers {
    aws = {
      version = ">= 4.23.0"
      source  = "hashicorp/aws"
    }
    local = {
      version = ">= 2.2.3"
      source  = "hashicorp/local"
    }
    tls = {
      version = ">= 4.0.1"
      source  = "hashicorp/tls"
    }
  }
}

provider "aws" {
  region                   = var.region
  shared_config_files      = var.aws_config_path
  shared_credentials_files = var.aws_credentials_path
  profile                  = var.profile
}

resource "aws_s3_bucket" "S3-Bucket" {
  bucket_prefix = var.bucket_prefix
  tags = {
    project = "aws_airflow" #edit if this is later used by airflow
  }
}

# resource "aws_security_group" "airflow_security_group" {
#   name = "airflow_security_group"
#   description = "Allow TLS inbound traffic"
# }

resource "aws_instance" "airflow_instance" {
  ami               = "ami-0d70546e43a941d70" # Ubuntu 22.04
  instance_type     = "t2.medium"
  availability_zone = var.AZ
  tags              = var.AIRFLOW_TAG
  # security_groups = #create securty group and reference
  key_name = aws_key_pair.ec2_key_pair.id
  # ebs_block_device {
  #   device_name = "/dev/sdh"
  #   delete_on_termination = false
  #   encrypted             = false
  #   tags                  = var.AIRFLOW_TAG
  #   volume_size           = 8
  #   volume_type           = "gp2"
  # }
}

# resource "aws_ebs_volume" "airflow_instance_volume" {
#   availability_zone = var.AZ
#   size              = 8
#   type              = "gp2" #general purpose ssd
# }

# resource "aws_volume_attachment" "airflow_ec2_ebs_attach" {
#   device_name = "/dev/sdh"
#   volume_id   = aws_ebs_volume.airflow_instance_volume.id
#   instance_id = aws_instance.airflow_instance.id
#   depends_on = [
#     aws_instance.airflow_instance,
#     aws_ebs_volume.airflow_instance_volume
#   ]
# }

resource "tls_private_key" "airflow_ec2_key" {
  algorithm = "RSA"
  rsa_bits  = 2048
}

resource "local_sensitive_file" "rsa" {
  filename        = "../.ssh/rsa_key"
  content         = tls_private_key.airflow_ec2_key.private_key_pem
  file_permission = 0400
}

resource "aws_key_pair" "ec2_key_pair" {
  key_name   = "airflow_instance_key_pair"
  public_key = tls_private_key.airflow_ec2_key.public_key_openssh
  tags       = var.AIRFLOW_TAG
}
