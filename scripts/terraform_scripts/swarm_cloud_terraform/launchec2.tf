resource "aws_instance" "k8s_master" {
  ami           = "ami-05640718ecb83f3c5" # Example AMI, replace with a Kubernetes supported one
  instance_type = "t3.medium"
  key_name      = aws_key_pair.ssh_key.key_name
  subnet_id     = aws_subnet.main.id  # Ensure this is the corrected subnet ID
  iam_instance_profile = aws_iam_instance_profile.ec2_instance_profile.name
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
  #Initiate the kubernetes network
  kubeadm init --pod-network-cidr=10.244.0.0/16
  mkdir -p $HOME/.kube
  cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
  chown $(id -u):$(id -g) $HOME/.kube/config

  # Apply network plugin if not already applied (idempotent operation)
  echo "Applying Flannel CNI plugin..."
  sudo kubectl apply -f https://raw.githubusercontent.com/coreos/flannel/master/Documentation/kube-flannel.yml
  # Wait for Flannel to be fully up
  sleep 30
  helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
  helm repo add grafana https://grafana.github.io/helm-charts
  helm repo update
  helm install prometheus prometheus-community/prometheus --namespace monitoring --create-namespace
  helm install grafana grafana/grafana --namespace monitoring --create-namespace
  JOIN_COMMAND=$(kubeadm token create --print-join-command)
  echo "$JOIN_COMMAND" > /tmp/k8s-join-command.sh
  aws s3 cp /tmp/k8s-join-command.sh s3://swarmskube/k8s-join-command.sh
  aws s3 cp /etc/kubernetes/admin.conf s3://swarmskube/kubeconfig

EOF
)
}

resource "aws_launch_template" "k8s_worker" {
  name_prefix = "k8s-worker-"
  image_id      = "ami-05640718ecb83f3c5" # Example AMI, replace with a Kubernetes supported one
  instance_type = "p3.2xlarge"
  key_name      = aws_key_pair.ssh_key.key_name

  iam_instance_profile {
    name = aws_iam_instance_profile.ec2_instance_profile.name
  }
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
