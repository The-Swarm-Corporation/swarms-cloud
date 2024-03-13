# IAM Role for Lambda execution
resource "aws_iam_role" "lambda_exec_role" {
  name = "lambda_execution_role"
  # Assume role policy and other configurations
}

# Attach policies to IAM Role for Lambda
# aws_iam_policy_attachment for AWSLambdaBasicExecutionRole and any other necessary policies

# Deploy API Gateway
resource "aws_api_gateway_deployment" "api_deployment" {
  rest_api_id = aws_api_gateway_rest_api.model_routing_api.id
  stage_name  = "prod"
  # Other configurations
}

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