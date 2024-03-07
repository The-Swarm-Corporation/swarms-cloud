provider "aws" {
  region = "us-east-1"
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

resource "aws_security_group" "model_api_sg" {
  name        = "model_api_sg"
  description = "Security group for model API EC2 instances"
  vpc_id      = aws_vpc.main.id

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

  enable_deletion_protection = false
}

resource "aws_launch_configuration" "model_api_conf" {
  name_prefix          = "model-api-"
  image_id             = "ami-0c574b811be1b656f"
  instance_type        = "p3.2xlarge" # Choose an appropriate instance type
  security_groups      = [aws_security_group.model_api_sg.id]
  iam_instance_profile = aws_iam_instance_profile.ssm.name

  user_data = <<-EOF
              #!/bin/bash
              sudo yum update -y
              sudo yum install -y docker
              sudo service docker start
              sudo usermod -a -G docker ec2-user
              sudo chkconfig docker on
              sudo yum install -y git
              git clone https://github.com/kyegomez/swarms-cloud.git
              cd swarms-cloud
              sudo docker build -t cogvlm .
              sudo docker run -d -p 8000:8000 cogvlm
              EOF

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_autoscaling_group" "model_api_asg" {
  launch_configuration = aws_launch_configuration.model_api_conf.id
  min_size             = 2
  max_size             = 10
  desired_capacity     = 2
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

  health_check {
    path     = "/"
    protocol = "HTTP"
    matcher  = "200"
  }
}

resource "aws_lb_listener" "model_api_listener" {
  load_balancer_arn = aws_lb.model_api_lb.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.model_api_tg.arn
  }
}
