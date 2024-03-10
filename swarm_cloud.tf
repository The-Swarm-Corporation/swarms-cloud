provider "aws" {
  region = "us-east-1"
}

resource "aws_key_pair" "ssh_key" {
  key_name   = "ec2_ssh_key"
  public_key = file("cog_rsa.pub") # path to your public key
}

resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true
}

resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.main.id
}

resource "aws_subnet" "main" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  map_public_ip_on_launch = true
  availability_zone       = "us-east-1a"
}

resource "aws_subnet" "main2" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.2.0/24"
  map_public_ip_on_launch = true
  availability_zone       = "us-east-1b"
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }
}


resource "aws_route_table_association" "public_main" {
  subnet_id      = aws_subnet.main.id
  route_table_id = aws_route_table.public.id
}

resource "aws_security_group" "model_api_sg" {
  name        = "model_api_sg"
  description = "Security group for model API EC2 instances"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # New ingress rule for SSH access
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # Adjust this to a more restricted CIDR block for enhanced security
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_iam_instance_profile" "ssm" {
  name = "ssm"
  role = aws_iam_role.ssm.name
}

resource "aws_iam_role" "ssm" {
  name = "ssm"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
        Effect = "Allow"
      },
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ssm" {
  role       = aws_iam_role.ssm.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_lb" "model_api_lb" {
  name               = "model-api-lb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.model_api_sg.id]
  subnets            = [aws_subnet.main.id, aws_subnet.main2.id]

  enable_deletion_protection = true
}

resource "aws_launch_configuration" "model_api_conf" {
  name_prefix          = "model-api-"
  image_id             = "ami-048eeb679c8e04a87"
  instance_type        = "p3.2xlarge" # Choose an appropriate instance type
  security_groups      = [aws_security_group.model_api_sg.id]
  iam_instance_profile = aws_iam_instance_profile.ssm.name
  key_name = aws_key_pair.ssh_key.key_name # Add this line

  root_block_device {
    volume_size           = 130
    delete_on_termination = true
    volume_type           = "gp2" # General Purpose SSD
  }

  user_data = <<-EOF
              #!/bin/bash
              sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit
              # Install the latest version of Docker CE and containerd
              sudo apt-get install -y docker-ce docker-ce-cli containerd.io
              sudo systemctl start docker
              sudo systemctl enable docker
              sudo usermod -aG docker ubuntu
              sudo docker pull public.ecr.aws/d6u1k1m2/cogvlmpub:latest
              sudo docker run --gpus all -d -p 8000:8000 public.ecr.aws/d6u1k1m2/cogvlmpub:latest
              EOF

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_autoscaling_group" "model_api_asg" {
  launch_configuration = aws_launch_configuration.model_api_conf.id
  min_size             = 1
  max_size             = 10
  desired_capacity     = 1
  vpc_zone_identifier  = [aws_subnet.main.id]

  target_group_arns = [aws_lb_target_group.model_api_tg.arn]

  tag {
    key                 = "Name"
    value               = "model-api-instance"
    propagate_at_launch = true
  }
}

resource "aws_lb_target_group" "model_api_tg" {
  name     = "model-api-tg"
  port     = 8000
  protocol = "HTTP"
  vpc_id   = aws_vpc.main.id

}

resource "aws_lb_listener" "model_api_listener" {
  load_balancer_arn = aws_lb.model_api_lb.arn
  port              = 8000
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.model_api_tg.arn
  }
}
