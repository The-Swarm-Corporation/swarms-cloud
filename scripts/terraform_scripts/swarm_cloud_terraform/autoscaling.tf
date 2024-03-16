resource "aws_autoscaling_group" "k8s_worker_asg" {
  launch_template {
    id      = aws_launch_template.k8s_worker.id
    version = "$Latest"
  }

  min_size         = 2
  max_size         = 10
  desired_capacity = 2

  vpc_zone_identifier = [aws_subnet.main.id, aws_subnet.main2.id]
  target_group_arns = [aws_lb_target_group.k8s_tg.arn]

  tag {
    key                 = "Name"
    value               = "KubernetesWorker"
    propagate_at_launch = true
  }
}