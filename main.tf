provider "aws" {
  region = "us-west-2"
}
resource "aws_acm_certificate" "cert" {
  domain_name       = "api.swarms.world"
  validation_method = "DNS"
  lifecycle {
    create_before_destroy = true
  }
  tags = {
    Name = "your_domain_certificate"
  }
}

resource "aws_route53_record" "cert_validation" {
  for_each = {
    for dvo in aws_acm_certificate.cert.domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  }

  zone_id = "Z0629215JQIY0GI18GHF" # Replace with your hosted zone ID
  name    = each.value.name
  type    = each.value.type
  records = [each.value.record]
  ttl     = 60
}
resource "aws_acm_certificate_validation" "cert" {
  certificate_arn         = aws_acm_certificate.cert.arn
  validation_record_fqdns = [for record in aws_route53_record.cert_validation : record.fqdn]
  depends_on = [aws_acm_certificate.cert]
}

resource "aws_route53_record" "lb_dns" {
  zone_id = "Z0629215JQIY0GI18GHF" # Replace with your hosted zone ID
  name    = "api.swarms.world"
  type    = "A"

  alias {
    name                   = aws_lb.model_api_lb.dns_name
    zone_id                = aws_lb.model_api_lb.zone_id
    evaluate_target_health = true
  }
}

resource "aws_route53_record" "yourdomain_caa_amazon" {
  zone_id = "Z0629215JQIY0GI18GHF"
  name    = "api.swarms.world"
  type    = "CAA"
  ttl     = "300"
  records = [
    "0 issue \"amazon.com\""
  ]
}

resource "aws_acm_certificate_validation" "model_api_cert" {
  certificate_arn         = aws_acm_certificate.cert.arn
  validation_record_fqdns = [for record in aws_route53_record.cert_validation : record.fqdn]
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
  availability_zone       = "us-west-2a"
}

resource "aws_subnet" "main2" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.2.0/24"
  map_public_ip_on_launch = true
  availability_zone       = "us-west-2b"
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

resource "aws_security_group" "model_lb_sg" {
  name        = "model_lb_sgwest"
  description = "Security group for model API EC2 instances"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Additional rule for HTTPS
  ingress {
    from_port   = 443
    to_port     = 443
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
  name               = "model-api-lbwest"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.model_lb_sg.id]
  subnets            = [aws_subnet.main.id, aws_subnet.main2.id]

  enable_deletion_protection = false
}


resource "aws_launch_configuration" "model_api_conf" {
  name_prefix          = "model-api-"
  image_id             = "ami-034b335fccb9ed729"
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
  name     = "model-api-tgwest"
  port     = 8000
  protocol = "HTTP"
  vpc_id   = aws_vpc.main.id

  stickiness {
    enabled = true
    type    = "lb_cookie"
    cookie_duration = 86400 # Duration in seconds, this example sets it to 1 day
  }
}
resource "aws_lb_listener" "http_redirect" {
  load_balancer_arn = aws_lb.model_api_lb.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type = "forward"
    target_group_arn = aws_lb_target_group.model_api_tg.arn
  }
}


resource "aws_lb_listener" "model_api_https_listener" {
  load_balancer_arn = aws_lb.model_api_lb.arn
  port              = 443
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-2016-08" # Default policy, adjust as needed
  certificate_arn   = aws_acm_certificate.cert.arn

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.model_api_tg.arn
  }
}
