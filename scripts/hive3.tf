provider "aws" {
  region = "us-west-2"
}

resource "aws_instance" "docker_vm" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"
  key_name      = "your-ssh-key-name"

  connection {
    type        = "ssh"
    user        = "ec2-user"
    private_key = file("${path.module}/your-ssh-key.pem")
    host        = self.public_ip
  }

  provisioner "remote-exec" {
    inline = [
      "sudo yum update -y",
      "sudo amazon-linux-extras install docker -y",
      "sudo service docker start",
      "sudo usermod -a -G docker ec2-user"
    ]
  }

  provisioner "remote-exec" {
    inline = [
      "cd /path/to/your/app",
      "sudo docker build -t my-app .",
      "sudo docker run -d -p 80:80 my-app"
    ]
  }

  tags = {
    Name = "DockerVM"
  }
}
