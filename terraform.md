# Terraform AWS Lambda and API Gateway Configuration

This Terraform configuration sets up an AWS infrastructure that includes Lambda functions and an API Gateway to expose those functions as HTTP endpoints. This is part of the backend for the `PLACEHOLDER_PROJECT_NAME` project.

## Overview

The configuration provisions the following resources:
- AWS IAM Role and Policy for Lambda execution and CloudWatch logging.
- AWS Lambda function to run the application code.
- AWS API Gateway to expose the Lambda function via HTTP endpoints.
- S3 Bucket Website Configuration for redirects.

## Requirements

- Terraform ~> 5.0
- AWS Provider ~> 3.0
- AWS CLI configured with appropriate access rights.

## Usage

To use this Terraform configuration:
1. Ensure AWS CLI is configured with the necessary access credentials.
2. Replace `PLACEHOLDER_PROJECT_NAME` and `PLACEHOLDER_REGION` with actual values in the configuration.
3. Initialize Terraform:
   ```bash
   terraform init
   ```
4. Apply the Terraform configuration:
   ```bash
   terraform apply
   ```

## Resources

- **aws_iam_role.lambda_role**: IAM Role for AWS Lambda execution with the necessary permissions.
- **aws_lambda_function.app**: The Lambda function containing the backend logic.
- **aws_api_gateway_rest_api.api**: The API Gateway setup for HTTP access to the Lambda function.
- **aws_api_gateway_deployment.deployment**: Deployment instance for the API Gateway.
- **aws_s3_bucket_website_configuration.redirect_bucket**: S3 Bucket configured for web hosting and redirects.
- **aws_iam_policy.cloudwatch_logs**: IAM Policy for logging to AWS CloudWatch.
- **aws_iam_role_policy_attachment.cloudwatch_logs_attachment**: Attaches the CloudWatch logging policy to the Lambda execution role.

## Outputs

- **api_url**: The URL of the deployed API Gateway endpoint. This URL is used to access the Lambda function over the web.

## Notes

- Ensure to replace `PLACEHOLDER_PROJECT_NAME` with your project's name to correctly configure resource names and references.
- `PLACEHOLDER_REGION` should be replaced with the AWS region you intend to deploy your resources in.
- It is recommended to manage sensitive information, such as AWS credentials and any other secrets, outside of this Terraform configuration for security reasons.
