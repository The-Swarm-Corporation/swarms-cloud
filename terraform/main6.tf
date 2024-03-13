
resource "aws_launch_template" "k8s_worker_lt" {
  name_prefix   = "k8s-worker-"
  image_id      = "ami-0c2b8ca1dad447f8a" # Example AMI, replace with a Kubernetes supported one
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
  ami           = "ami-0c2b8ca1dad447f8a" # Example AMI, replace with a Kubernetes supported one
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
  ami           = "ami-0c2b8ca1dad447f8a" # Example AMI, replace with a Kubernetes supported one
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
