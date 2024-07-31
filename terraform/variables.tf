variable "api_gateway_name" {
  type        = string
  description = "The name of the API Gateway"
  default     = "aws-permissions-bot"
}

variable "backend_lambda_name" {
  type        = string
  description = "The name of the backend Lambda function"
  default     = "aws-permissions-bot-backend"
}

variable "invocation_lambda_name" {
  type        = string
  description = "The name of the invocation Lambda function"
  default     = "aws-permissions-bot-invocation"
}

variable "secrets_arn_list" {
  type        = list(string)
  description = "A list of ARNs (Amazon Resource Names) of the AWS Secrets Manager secrets that the Lambda function will use to access sensitive data."
}

variable "endpoint_type" {
  type        = string
  default     = "REGIONAL"
  description = "Type of the endpoint for the REST API. Valid values: EDGE or REGIONAL. If unspecified, defaults to EDGE."

  validation {
    condition     = contains(["EDGE", "REGIONAL"], var.endpoint_type)
    error_message = "The endpoint_type must be one of 'EDGE' or 'REGIONAL'."
  }
}

variable "api_path" {
  type        = string
  default     = "/api/user-interaction"
  description = "The path on the API Gateway where the POST request is accepted and routed to the SQS queue."
}

variable "log_level" {
  type        = string
  default     = "INFO"
  description = "The logging level for the API Gateway. Valid values: OFF, ERROR or INFO. If unspecified, defaults to INFO."

  validation {
    condition     = contains(["OFF", "ERROR", "INFO"], var.log_level)
    error_message = "The log_level must be one of 'OFF', 'ERROR' or 'INFO'."
  }
}

variable "full_debug_mode" {
  type        = bool
  default     = false
  description = "Enables detailed logging for all events in API Gateway. This may include sensitive data, so use with caution. Useful for troubleshooting purposes."
}

variable "execution_logs_retention" {
  description = "The number of days to retain the log events in the specified log group. Possible values are: 1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365, 400, 545, 731, 1096, 1827, 2192, 2557, 2922, 3288, 3653, and 0. If you select 0, the events in the log group are always retained and never expire."
  type        = number
  default     = 90

  validation {
    condition     = contains([0, 1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365, 400, 545, 731, 1096, 1827, 2192, 2557, 2922, 3288, 3653], var.execution_logs_retention)
    error_message = "The retention period must be one of the following values: 0, 1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365, 400, 545, 731, 1096, 1827, 2192, 2557, 2922, 3288, 3653."
  }
}

variable "lambda_logs_retention" {
  description = "The number of days to retain the log events in the specified log group. Possible values are: 1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365, 400, 545, 731, 1096, 1827, 2192, 2557, 2922, 3288, 3653, and 0. If you select 0, the events in the log group are always retained and never expire."
  type        = number
  default     = 90

  validation {
    condition     = contains([0, 1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365, 400, 545, 731, 1096, 1827, 2192, 2557, 2922, 3288, 3653], var.lambda_logs_retention)
    error_message = "The retention period must be one of the following values: 0, 1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365, 400, 545, 731, 1096, 1827, 2192, 2557, 2922, 3288, 3653."
  }
}

variable "create_apigw_logs_account_role" {
  type        = bool
  default     = false
  description = "Determines whether to create an IAM role at the account level that allows API Gateway to write logs. Generally, this should be created once per AWS account."
}

variable "waf_arn" {
  type        = string
  description = "The ARN (Amazon Resource Name) of the AWS WAF (Web Application Firewall) to associate with the API Gateway."
}

variable "tags" {
  type = map(string)
  default = {
    "managed_by"   = "terraform"
    "project_name" = "aws-permissions-bot"
  }
  description = "A map of key-value pairs to assign as metadata tags to all resources created by the Terraform script. Useful for cost tracking, ownership identification, etc."
}

variable "security_scanner_role_name" {
  type        = string
  description = "The name of the IAM role that the security scanner Lambda function will assume to list account resources."
  default     = "SecurityAuditRole"
}