provider "aws" {
  region = "us-east-1"
}
resource "aws_key_pair" "ssh_key" {
  key_name   = "ec2_ssh_key2"
  public_key = file("cog_rsa.pub") # path to your public key
}
resource "null_resource" "init_k8s_cluster" {
  depends_on = [aws_instance.k8s_master]

  provisioner "local-exec" {
    command = <<-EOT
      echo "Waiting for kubeconfig to be uploaded to S3..."
      while ! aws s3 ls "s3://swarmskube/kubeconfig"; do
        sleep 30
        echo "Waiting for kubeconfig..."
      done
      echo "Kubeconfig found. Downloading..."
      aws s3 cp "s3://swarmskube/kubeconfig" "${path.module}/kubeconfig"

      echo "Waiting for Kubernetes nodes to be ready..."
      until kubectl --kubeconfig="${path.module}/kubeconfig" get nodes; do 
        echo "Waiting for k8s to be ready..."
        sleep 30
      done
    EOT
    environment = {
      AWS_DEFAULT_REGION = "us-east-1"
      KUBECONFIG         = "${path.module}/kubeconfig"
    }
  }
}


provider "kubernetes" {
  config_path = "${path.module}/kubeconfig"
}