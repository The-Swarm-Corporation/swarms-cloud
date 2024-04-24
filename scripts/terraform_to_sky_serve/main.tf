provider "aws" {
  region = "us-east-1"
}

# Create a new VPC
resource "aws_vpc" "swarms_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name = "SwarmsVPC"
  }
}

# Create an Internet Gateway for the VPC
resource "aws_internet_gateway" "swarms_igw" {
  vpc_id = aws_vpc.swarms_vpc.id

  tags = {
    Name = "SwarmsIGW"
  }
}

# Create a subnet within the VPC
resource "aws_subnet" "swarms_subnet" {
  vpc_id            = aws_vpc.swarms_vpc.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "us-east-1a"

  map_public_ip_on_launch = true

  tags = {
    Name = "SwarmsSubnet"
  }
}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "swarms_log_group" {
  name              = "/ec2/swarms/logs"
  retention_in_days = 14
}

# CloudWatch Log Stream
resource "aws_cloudwatch_log_stream" "swarms_log_stream" {
  name           = "InstanceLogStream"
  log_group_name = aws_cloudwatch_log_group.swarms_log_group.name
}


# Create a security group in the VPC
resource "aws_security_group" "swarms_sg" {
  name        = "swarms-sg"
  description = "Security Group for EC2 Instances in Swarms VPC"
  vpc_id      = aws_vpc.swarms_vpc.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "swarms-sg"
  }
}

# Create a Route 53 hosted zone
resource "aws_route53_zone" "swarms_zone" {
  name = "api.swarms.world"
}

# EC2 Instance using the created resources
resource "aws_instance" "swarms_ec2" {
  ami                         = "ami-0ac1f653c5b6af751" # Specify the correct AMI ID
  instance_type               = "m6i.xlarge"
  subnet_id                   = aws_subnet.swarms_subnet.id
  key_name                    = "your-key-name" # Update with your actual key name
  vpc_security_group_ids      = [aws_security_group.swarms_sg.id]
  associate_public_ip_address = true

  tags = {
    Name = "sky-sky-serve-controller-3f665020-3f66-head"
  }
}

# Route 53 Record to point to the EC2 instance
resource "aws_route53_record" "swarms_record" {
  zone_id = aws_route53_zone.swarms_zone.zone_id
  name    = "api.swarms.world"
  type    = "A"
  ttl     = "300"
  records = [aws_instance.swarms_ec2.public_ip]
}
