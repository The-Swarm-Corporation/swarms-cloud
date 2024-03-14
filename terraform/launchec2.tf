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
              # Generate the join command and upload to S3
              JOIN_COMMAND=$(kubeadm token create --print-join-command)
              echo "$JOIN_COMMAND" > /tmp/k8s-join-command.sh
              aws s3 cp /tmp/k8s-join-command.sh s3://swarmskube/k8s-join-command.sh
              EOF
}

resource "aws_instance" "k8s_worker" {
  count         = 2 # Number of worker nodes
  ami           = "ami-0fb87c49e4c052ef5" # Example AMI, replace with a Kubernetes supported one
  instance_type = "p3.2xlarge"
  key_name      = aws_key_pair.ssh_key.key_name

  vpc_security_group_ids = [aws_security_group.k8s_worker_sg.id]

  tags = {
    Name = "KubernetesWorker"
  }

  user_data = <<-EOF
              #!/bin/bash
              # Download and execute the Kubernetes join command securely
              aws s3 cp s3://swarmskube/k8s-join-command.sh /tmp/k8s-join-command.sh
              chmod +x /tmp/k8s-join-command.sh
              /tmp/k8s-join-command.sh
              EOF
}
