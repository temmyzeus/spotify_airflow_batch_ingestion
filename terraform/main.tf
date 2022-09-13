resource "aws_s3_bucket" "bucket" {
  bucket = "${var.bucket_prefix}-${data.aws_caller_identity.account_details.account_id}"
  tags = {
    Project = "Spotify"
  }
}

resource "aws_vpc" "vpc" {
  cidr_block           = "10.123.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    "Name" = "spotify-project-airflow-vpc"
  }
}

resource "aws_subnet" "subnet" {
  vpc_id                  = aws_vpc.vpc.id
  cidr_block              = "10.123.1.0/24"
  map_public_ip_on_launch = true
  availability_zone       = var.AZ
  tags = {
    "Name" = "spotify-project-airflow-subnet"
  }
}

resource "aws_internet_gateway" "internet_gateway" {
  vpc_id = aws_vpc.vpc.id
  tags = {
    "Name" = "spotify-project-airflow-ig"
  }
}

resource "aws_route_table" "route_table" {
  vpc_id = aws_vpc.vpc.id
  tags = {
    "Name" = "spotify-project-airflow-rt"
  }
}

resource "aws_route" "default_route" {
  route_table_id         = aws_route_table.route_table.id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.internet_gateway.id
}

resource "aws_route_table_association" "name" {
  route_table_id = aws_route_table.route_table.id
  subnet_id      = aws_subnet.subnet.id
}

resource "aws_security_group" "security_group" {
  name        = "spotify-project-airflow-security-group"
  description = "Allow TLS inbound traffic"
}

resource "aws_security_group" "sg" {
  name        = "spotify-project-airflow-sg"
  description = "Spotify Project Security Group"
  vpc_id      = aws_vpc.vpc.id
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  # Add engress for port 8080, 7900, 5900, 4444 and others
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Access the open internet"
  }
  tags = {
    "Name" = "spotify-project-security-group"
  }
}

resource "aws_instance" "ec2_instance" {
  ami                         = data.aws_ami.ec2_server_ami.id
  instance_type               = "t2.medium"
  availability_zone           = var.AZ
  tags                        = var.AIRFLOW_TAG
  key_name                    = aws_key_pair.ec2_key_pair.key_name
  vpc_security_group_ids      = [aws_security_group.sg.id]
  subnet_id                   = aws_subnet.subnet.id
  user_data                   = file("setup-instance.tpl")
  user_data_replace_on_change = true
  root_block_device {
    volume_size = 10
  }
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

resource "aws_key_pair" "ec2_key_pair" {
  key_name   = "spotify-project-airflow-instance-key-pair"
  public_key = file(var.ssh_key_file)
  tags       = var.AIRFLOW_TAG
}

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
  depends_on = [
    aws_key_pair.ec2_key_pair
  ]
  tags = {
    Project : "Spotify"
  }
}
