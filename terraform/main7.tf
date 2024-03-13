
resource "aws_autoscaling_group" "model_api_asg" {
  launch_configuration = aws_launch_configuration.model_api_conf.id
  min_size             = 1
  max_size             = 10
  desired_capacity     = 1
  vpc_zone_identifier  = [aws_subnet.main.id]

  target_group_arns = [aws_lb_target_group.model_api_tg.arn]

  tag {
    key                 = "Name"
    value               = "model-api-instance"
    propagate_at_launch = true
  }
}

resource "aws_autoscaling_group" "k8s_worker_asg" {
  launch_template {
    id      = aws_launch_template.k8s_worker_lt.id
    version = "$Latest"
  }

  min_size         = 2
  max_size         = 5
  desired_capacity = 2

  vpc_zone_identifier = [aws_subnet.main.id, aws_subnet.main2.id]

  tag {
    key                 = "Name"
    value               = "KubernetesWorker"
    propagate_at_launch = true
  }
}
