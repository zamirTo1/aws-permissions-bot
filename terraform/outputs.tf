output "log_group_name" {
  description = "The name of the CloudWatch Log Group associated with the API Gateway."
  value       = aws_cloudwatch_log_group.log_group.name
}

output "api_id" {
  description = "The ID of the API Gateway."
  value       = aws_api_gateway_rest_api.api.id
}
