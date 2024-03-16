# Outputs for important endpoints or ARNs
output "cogvlm_service_url" {
  value = kubernetes_service.cogvlm_service.status.0.load_balancer.0.ingress.0.hostname
}

output "qwenvl_service_url" {
  value = kubernetes_service.qwenvl_service.status.0.load_balancer.0.ingress.0.hostname
}

output "api_gateway_invoke_url" {
  value = aws_api_gateway_deployment.api_deployment.invoke_url
}