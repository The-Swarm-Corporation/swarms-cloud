provider "aws" {
  region = "us-east-1"
}

resource "aws_key_pair" "ssh_key" {
  key_name   = "ec2_ssh_key"
  public_key = file("cog_rsa.pub") # path to your public key
}
resource "null_resource" "wait_for_k8s" {
  depends_on = [aws_instance.k8s_master]

  provisioner "local-exec" {
    command = "until kubectl get nodes; do echo waiting for k8s to be ready; sleep 30; done"
    environment = {
      KUBECONFIG = "${path.module}/kubeconfig"
    }
  }
}