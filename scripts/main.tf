provider "aws" {
  region = "us-east-1" # Specify your AWS region
}

# Create a new VPC
resource "aws_vpc" "custom_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true
}

# Create public subnets
resource "aws_subnet" "public_subnet" {
  count                   = 2
  vpc_id                  = aws_vpc.custom_vpc.id
  cidr_block              = "10.0.1.${count.index * 64}/26"
  map_public_ip_on_launch = true
  availability_zone       = element(["us-east-1a", "us-east-1b"], count.index)
}
# Create an internet gateway
resource "aws_internet_gateway" "gw" {
  vpc_id = aws_vpc.custom_vpc.id
}

# Create a route table for public subnets
resource "aws_route_table" "public_route_table" {
  vpc_id = aws_vpc.custom_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.gw.id
  }
}

# Associate public subnets with route table
resource "aws_route_table_association" "public_rta" {
  count          = length(aws_subnet.public_subnet.*.id)
  subnet_id      = element(aws_subnet.public_subnet.*.id, count.index)
  route_table_id = aws_route_table.public_route_table.id
}


# Create a security group for the load balancer
resource "aws_security_group" "alb_sg" {
  name        = "alb-sg"
  description = "Security group for ALB"
  vpc_id      = aws_vpc.custom_vpc.id

  # Allow inbound HTTP access
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Allow all outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Create a security group for ECS instances
resource "aws_security_group" "ecs_instances_sg" {
  name        = "ecs-instances-sg"
  description = "Security group for ECS instances"
  vpc_id      = aws_vpc.custom_vpc.id

  # Allow inbound traffic from the ALB security group on port 8000
  ingress {
    from_port       = 8000
    to_port         = 8000
    protocol        = "tcp"
    security_groups = [aws_security_group.alb_sg.id]
  }

  # Allow all outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}


resource "aws_launch_template" "ecs_lt" {
  name          = "ecs-launch-template3"
  image_id      = "ami-0c55b159cbfafe1f0" # Specify the correct AMI for your ECS instances
  instance_type = "t2.xlarge"

  block_device_mappings {
    device_name = "/dev/sda1"

    ebs {
      volume_size = 75
    }
  }

  iam_instance_profile {
    name = aws_iam_instance_profile.ecs_instance_profile.name
  }
user_data = base64encode(<<-EOF
              #!/bin/bash
              echo "ECS_CLUSTER=my-app-cluster2" >> /etc/ecs/ecs.config
              EOF
)

  lifecycle {
    create_before_destroy = true
  }
}
resource "aws_ecs_cluster" "my_cluster" {
  name = "my-app-cluster2"
}
resource "aws_autoscaling_group" "ecs_asg" {
  min_size             = 1
  max_size             = 3
  launch_template {
    id = aws_launch_template.ecs_lt.id
    version = "$Latest"
  }

  vpc_zone_identifier = aws_subnet.public_subnet.*.id # Specify subnets for your instances

  tag {
    key                 = "Name"
    value               = "ECS Instance"
    propagate_at_launch = true
  }
}

# IAM role for ECS instances
resource "aws_iam_role" "ecs_instance_role" {
  name = "ecsInstanceRole2"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole",
        Principal = {
          Service = "ec2.amazonaws.com"
        },
        Effect = "Allow",
        Sid    = ""
      },
    ]
  })

  # Attach the necessary policies for ECS
}

resource "aws_iam_instance_profile" "ecs_instance_profile" {
  name = "ecsInstanceProfile2"
  role = aws_iam_role.ecs_instance_role.name
}
# IAM Role for ECS tasks - allows EC2 instances to pull Docker images
resource "aws_iam_role" "ecs_task_execution_role" {
  name = "ecs_task_execution_role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action = "sts:AssumeRole",
      Effect = "Allow",
      Principal = {
        Service = "ecs-tasks.amazonaws.com",
      },
    }],
  })
}

# Attach the necessary policies to the ECS instance role
resource "aws_iam_role_policy_attachment" "ecs_instance_role_policy_attachment" {
  role       = aws_iam_role.ecs_instance_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonEC2ContainerServiceforEC2Role"
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution_role_policy_attachment" {
  role      = aws_iam_role.ecs_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}


# Update your load balancer to use the new public subnets and security group
resource "aws_lb" "app_lb" {
  name               = "app-lb2"
  internal           = false
  load_balancer_type = "application"
  subnets            = aws_subnet.public_subnet.*.id
  security_groups    = [aws_security_group.alb_sg.id]
}
resource "aws_lb_target_group" "app_tg" {
  name        = "app-tg2"
  protocol    = "HTTP"
  port        = 80
  vpc_id      = aws_vpc.custom_vpc.id
  target_type = "ip"
}

# Target Group for the ALB
resource "aws_lb_listener" "app_listener" {
  load_balancer_arn = aws_lb.app_lb.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.app_tg.arn
  }
}


resource "aws_ecs_service" "app_service" {
  name            = "my-app-service2"
  cluster         = aws_ecs_cluster.my_cluster.id
  task_definition = aws_ecs_task_definition.app_task.arn
  desired_count   = 1
  launch_type     = "EC2"

  network_configuration {
    subnets          = aws_subnet.public_subnet.*.id
    security_groups  = [aws_security_group.ecs_instances_sg.id]
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.app_tg.arn
    container_name   = "app-container"
    container_port   = 80
  }

  depends_on = [
    aws_lb_listener.app_listener,
  ]
}
# ECS Task Definition with a simple container definition
resource "aws_ecs_task_definition" "app_task" {
  family                   = "app-task-family2"
  network_mode             = "awsvpc"
  requires_compatibilities = ["EC2"]  
  execution_role_arn       = "arn:aws:iam::916723593639:role/ecs_task_execution_role"
  #execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  cpu       = 2048
  memory    = 4096
  container_definitions = jsonencode([{
    name      = "app-container"
    image     = "916723593639.dkr.ecr.us-east-1.amazonaws.com/qwenfastapi:latest"
    cpu       = 2048
    memory    = 4096 
    essential = true,
    portMappings = [{
      containerPort = 80
      protocol      = "tcp"
    }]
  }])
}