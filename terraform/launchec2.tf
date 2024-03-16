resource "aws_instance" "k8s_master" {
  ami           = "ami-0df2ee7e95cf003c5" # Example AMI, replace with a Kubernetes supported one
  instance_type = "t3.medium"
  key_name      = aws_key_pair.ssh_key.key_name
  subnet_id     = aws_subnet.main.id  # Ensure this is the corrected subnet ID
  vpc_security_group_ids = [aws_security_group.k8s_master_sg.id]

  tags = {
    Name = "KubernetesMaster"
  }

user_data = base64encode(<<-EOF
  #!/bin/bash

  # Log the status of Docker and Kubernetes services
  echo "Checking the status of Docker service..."
  sudo systemctl status docker | sudo tee /var/log/docker-status.log > /dev/null

  echo "Checking the status of kubelet service..."
  sudo systemctl status kubelet | sudo tee /var/log/kubelet-status.log > /dev/null

  # Ensure Docker and kubelet services are started
  echo "Ensuring Docker service is running..."
  sudo systemctl enable --now docker

  echo "Ensuring kubelet service is running..."
  sudo systemctl enable --now kubelet

  # Log Kubernetes cluster status
  echo "Logging Kubernetes cluster status..."
  sudo kubectl cluster-info | sudo tee /var/log/kubectl-cluster-info.log > /dev/null

  # Check for any not running system pods
  echo "Checking for any not running system pods..."
  sudo kubectl get pods --all-namespaces | grep -v Running | sudo tee /var/log/kubectl-non-running-pods.log > /dev/null

  # Apply network plugin if not already applied (idempotent operation)
  echo "Applying Flannel CNI plugin..."
  sudo kubectl apply -f https://raw.githubusercontent.com/coreos/flannel/master/Documentation/kube-flannel.yml
  JOIN_COMMAND=$(kubeadm token create --print-join-command)
  echo "$JOIN_COMMAND" > /tmp/k8s-join-command.sh
  aws s3 cp /tmp/k8s-join-command.sh s3://swarmskube/k8s-join-command.sh
EOF
)
}

resource "aws_launch_template" "k8s_worker" {
  name_prefix = "k8s-worker-"
  image_id      = "ami-0fb87c49e4c052ef5" # Example AMI, replace with a Kubernetes supported one
  instance_type = "p3.2xlarge"
  key_name      = aws_key_pair.ssh_key.key_name

  vpc_security_group_ids = [aws_security_group.k8s_worker_sg.id]


  user_data = base64encode(<<-EOF
              #!/bin/bash
              # Download and execute the Kubernetes join command securely
              
              while true; do
                if aws s3 ls "s3://swarmskube/k8s-join-command.sh"; then
                  aws s3 cp s3://swarmskube/k8s-join-command.sh /tmp/k8s-join-command.sh
                  chmod +x /tmp/k8s-join-command.sh
                  /tmp/k8s-join-command.sh
                  break
                else
                  echo "Waiting for the master node to initialize..."
                  sleep 30
                fi
              done
              EOF
  )

              
  tags = {
    resource_type = "instance"
    Name = "KubernetesWorker"
  }
}
