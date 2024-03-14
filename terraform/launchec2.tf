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

resource "aws_launch_template" "k8s_worker_lt" {
  name_prefix   = "k8s-worker-"
  image_id      = "ami-0fb87c49e4c052ef5" # Example AMI, replace with a Kubernetes supported one
  instance_type = "t3.medium"
  key_name      = aws_key_pair.ssh_key.key_name

  user_data = base64encode(<<-EOF
              #!/bin/bash
              # Placeholder for worker join commands. This will be replaced dynamically.
              EOF)

  vpc_security_group_ids = [aws_security_group.k8s_worker_sg.id]

  tag_specifications {
    resource_type = "instance"
    tags = {
      Name = "KubernetesWorker"
    }
  }
}

resource "aws_instance" "k8s_master" {
  ami           = "ami-0fb87c49e4c052ef5" # Example AMI, replace with a Kubernetes supported one
  instance_type = "t3.medium"
  key_name      = aws_key_pair.ssh_key.key_name

  tags = {
    Name = "KubernetesMaster"
  }

  user_data = <<-EOF
              #!/bin/bash
              # Initialize Kubernetes Master Node
              sudo kubeadm init --pod-network-cidr=192.168.0.0/16
              mkdir -p $HOME/.kube
              sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
              sudo chown $(id -u):$(id -g) $HOME/.kube/config
              # Install Flannel networking
              kubectl apply -f https://raw.githubusercontent.com/coreos/flannel/master/Documentation/kube-flannel.yml
              EOF
}

resource "aws_instance" "k8s_worker" {
  count         = 2 # Number of worker nodes
  ami           = "ami-0fb87c49e4c052ef5" # Example AMI, replace with a Kubernetes supported one
  instance_type = "t3.medium"
  key_name      = aws_key_pair.ssh_key.key_name

  tags = {
    Name = "KubernetesWorker"
  }

  user_data = <<-EOF
              #!/bin/bash
              # Commands to join the worker nodes to the Kubernetes cluster will be executed manually or could be automated with additional scripting
              EOF
}
