# AWS Lambda function for request routing
resource "aws_lambda_function" "request_router" {
  function_name = "requestRouter"
  # other configurations like handler, runtime, and environment variables
  # Your function's source code would route the requests based on the model name
  environment {
    variables = {
      COGVLM_ENDPOINT = "http://model1-service",
      QWENVL_ENDPOINT = "http://model2-service",
      // Add more environment variables as necessary
    }
  }
}


# API Gateway to expose the Lambda Function
resource "aws_api_gateway_rest_api" "model_routing_api" {
  name        = "ModelRoutingAPI"
  description = "API Gateway to route model requests"
}

resource "aws_api_gateway_resource" "model_routing_resource" {
  rest_api_id = aws_api_gateway_rest_api.model_routing_api.id
  parent_id   = aws_api_gateway_rest_api.model_routing_api.root_resource_id
  path_part   = "{proxy+}" # Enable proxy resource to capture all sub-paths
}

resource "aws_api_gateway_method" "model_post_method" {
  rest_api_id   = aws_api_gateway_rest_api.model_routing_api.id
  resource_id   = aws_api_gateway_resource.model_routing_resource.id
  http_method   = "ANY" # Accept any HTTP method
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "model_lambda_integration" {
  rest_api_id = aws_api_gateway_rest_api.model_routing_api.id
  resource_id = aws_api_gateway_resource.model_routing_resource.id
  http_method = aws_api_gateway_method.model_post_method.http_method

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.request_router.invoke_arn
}


