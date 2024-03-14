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
