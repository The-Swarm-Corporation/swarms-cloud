
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
