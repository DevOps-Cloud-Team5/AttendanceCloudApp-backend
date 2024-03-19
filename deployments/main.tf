terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  backend "s3" {
    bucket = "PLACEHOLDER_PROJECT_NAME-terraform"
    key    = "terraform.tfstate"
    region = "PLACEHOLDER_REGION"
    acl = "bucket-owner-full-control"
  }
}

provider "aws" {
  region = "PLACEHOLDER_REGION"
}

resource "aws_iam_role" "lambda_role" {
  name = "lambda_role_zappa_tf"
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

resource "aws_lambda_function" "app" {
  function_name = "PLACEHOLDER_PROJECT_NAME-tf"
  handler       = "handler.lambda_handler"
  runtime       = "python3.10"
  timeout       = 30
  memory_size = 1024

  filename         = "${path.module}/../package.zip"
  source_code_hash = filebase64sha256("${path.module}/../package.zip")
  role             = aws_iam_role.lambda_role.arn
}

resource "aws_api_gateway_rest_api" "api" {
  name        = "zappa-app-api"
  description = "API for zappa tf app"
  binary_media_types = ["*/*"]
}

resource "aws_api_gateway_deployment" "deployment" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  stage_name  = "prod"

  lifecycle {
    create_before_destroy = true
  }

  depends_on = [
    aws_api_gateway_integration.proxy,
    aws_api_gateway_integration.root,
  ]
}

resource "aws_api_gateway_method" "root" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_rest_api.api.root_resource_id
  http_method   = "ANY"
  authorization = "NONE"

  request_parameters = {
    "method.request.header.Content-Type" = true
    "method.request.header.Accept"       = true
  }
}

resource "aws_api_gateway_integration" "root" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_rest_api.api.root_resource_id
  http_method = aws_api_gateway_method.root.http_method
  timeout_milliseconds = 29000

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.app.invoke_arn
}

resource "aws_api_gateway_resource" "proxy" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_rest_api.api.root_resource_id
  path_part   = "{proxy+}"
}

resource "aws_api_gateway_method" "proxy" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.proxy.id
  http_method   = "ANY"
  authorization = "NONE"

  request_parameters = {
    "method.request.header.Content-Type" = true
    "method.request.header.Accept"       = true
  }
}

resource "aws_api_gateway_integration" "proxy" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.proxy.id
  http_method = aws_api_gateway_method.proxy.http_method

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.app.invoke_arn
}

resource "aws_lambda_permission" "apigw" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.app.function_name
  principal     = "apigateway.amazonaws.com"

  # The /*/* portion grants permission to all methods on all resources within the API.
  source_arn = "${aws_api_gateway_rest_api.api.execution_arn}/*/*"
}

resource "aws_iam_policy" "cloudwatch_logs" {
  name        = "LambdaCloudWatchLogsPolicy_zappa"
  description = "Allows Lambda function to write logs to CloudWatch Logs"
  policy      = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Effect": "Allow",
      "Resource": "*"
    }
  ]
}
EOF
}

resource "aws_s3_bucket_website_configuration" "redirect_bucket" {
  bucket = "PLACEHOLDER_PROJECT_NAME-redirect"

  redirect_all_requests_to {
    host_name = "${aws_api_gateway_rest_api.api.id}.execute-api.PLACEHOLDER_REGION.amazonaws.com"
    protocol = "https"
  }
}

resource "aws_iam_role_policy_attachment" "cloudwatch_logs_attachment" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.cloudwatch_logs.arn
}

output "api_url" {
  value       = "https://${aws_api_gateway_rest_api.api.id}.execute-api.PLACEHOLDER_REGION.amazonaws.com/${aws_api_gateway_deployment.deployment.stage_name}"
  description = "The URL of the API endpoint"
}