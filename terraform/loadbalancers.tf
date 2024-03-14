resource "aws_lb" "k8s_nlb" {
  name               = "k8s-nlb"
  internal           = false
  load_balancer_type = "network"
  subnets            = [aws_subnet.main.id, aws_subnet.main2.id]

  enable_deletion_protection = false
}

# Define a listener for the NLB
resource "aws_lb_listener" "front_end" {
  load_balancer_arn = aws_lb.k8s_nlb.arn
  protocol          = "TCP"
  port              = "80"
  
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.k8s_tg.arn
  }
}

# Define a target group for the NLB that points to your K8s service NodePort
resource "aws_lb_target_group" "k8s_tg" {
  name     = "k8s-tg"
  port     = 30000 # Example NodePort
  protocol = "TCP"
  vpc_id   = aws_vpc.main.id
  
  health_check {
    protocol = "TCP"
    port     = "traffic-port"
  }
}

# Assuming you have EC2 instances tagged as Kubernetes workers
resource "aws_lb_target_group_attachment" "k8s_tg_attachment" {
  target_group_arn = aws_lb_target_group.k8s_tg.arn
  target_id        = aws_instance.k8s_worker.id # You'll need to adjust this based on how you've set up your instances
  port             = 30000
}



resource "aws_lb" "model_api_lb" {
  name               = "model-api-lb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.model_api_sg.id]
  subnets            = [aws_subnet.main.id, aws_subnet.main2.id]

  enable_deletion_protection = true
}

