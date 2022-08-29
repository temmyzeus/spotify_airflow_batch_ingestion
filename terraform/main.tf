resource "aws_s3_bucket" "S3-Bucket" {
  bucket = "${var.bucket_prefix}-${data.aws_caller_identity.account_details.account_id}"
  tags = {
    Project = "Spotify"
  }
}

# resource "aws_security_group" "airflow_security_group" {
#   name = "airflow_security_group"
#   description = "Allow TLS inbound traffic"
# }

# resource "aws_instance" "airflow_instance" {
#   ami               = "ami-0d70546e43a941d70" # Ubuntu 22.04
#   instance_type     = "t2.medium"
#   availability_zone = var.AZ
#   tags              = var.AIRFLOW_TAG
#   # security_groups = #create securty group and reference
#   key_name = aws_key_pair.ec2_key_pair.id
# ebs_block_device {
#   device_name = "/dev/sdh"
#   delete_on_termination = false
#   encrypted             = false
#   tags                  = var.AIRFLOW_TAG
#   volume_size           = 8
#   volume_type           = "gp2"
# }
# }

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

# resource "tls_private_key" "airflow_ec2_key" {
#   algorithm = "RSA"
#   rsa_bits  = 2048
# }

# resource "local_sensitive_file" "rsa" {
#   filename        = "../.ssh/rsa_key"
#   content         = tls_private_key.airflow_ec2_key.private_key_pem
#   file_permission = 0400
# }

# resource "aws_key_pair" "ec2_key_pair" {
#   key_name   = "airflow_instance_key_pair"
#   public_key = tls_private_key.airflow_ec2_key.public_key_openssh
#   tags       = var.AIRFLOW_TAG
# }

resource "aws_db_instance" "spotify_db" {
  engine                    = "postgres"
  engine_version            = "14.2"
  db_name                   = "SpotifyDB"
  availability_zone         = var.AZ
  identifier                = "spotify-db"
  username                  = var.DATABASE_USERNAME
  password                  = var.DATABASE_PASSWD
  instance_class            = "db.t3.micro"
  storage_type              = "gp2"
  allocated_storage         = 10
  max_allocated_storage     = 15
  skip_final_snapshot       = false
  final_snapshot_identifier = "spotify-db-snapshot"
  tags = {
    Project : "Spotify"
  }
}
