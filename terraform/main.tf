data "aws_region" "current" {}
data "aws_caller_identity" "current" {}

locals {
  stage_name = "live"
}

# Set account log settings if needed
resource "aws_iam_role" "apigw_logs_account_role" {
  count = var.create_apigw_logs_account_role ? 1 : 0
  name  = "AmazonAPIGatewayPushToCloudWatchLogs"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Sid    = "AllowAssumeByAPIGW"
        Effect = "Allow"
        Principal = {
          Service = "apigateway.amazonaws.com"
        },
        Action = "sts:AssumeRole"
      },
    ]
  })
  managed_policy_arns = [
    "arn:aws:iam::aws:policy/service-role/AmazonAPIGatewayPushToCloudWatchLogs"
  ]
  tags = var.tags
}

resource "aws_api_gateway_account" "create_apigw_logs_account_role_association" {
  count               = var.create_apigw_logs_account_role ? 1 : 0
  cloudwatch_role_arn = aws_iam_role.apigw_logs_account_role[0].arn
}

# Create log group for execution logs
resource "aws_cloudwatch_log_group" "log_group" {
  name              = "API-Gateway-Execution-Logs_${aws_api_gateway_rest_api.api.id}/${local.stage_name}"
  retention_in_days = var.execution_logs_retention
}

resource "aws_api_gateway_rest_api" "api" {
  name                         = var.api_gateway_name
  description                  = "REST API Gateway for ${var.api_gateway_name}."
  disable_execute_api_endpoint = false

  body = jsonencode({
    openapi = "3.0.1"
    info = {
      title   = var.api_gateway_name
      version = "1.0"
    }
    "paths" : {
      "/slack/command" : {
        "post" : {
          "responses" : {
            "200" : {
              "description" : "200 response",
              "content" : {
                "application/json" : {
                  "schema" : {
                    "$ref" : "#/components/schemas/Empty"
                  }
                }
              }
            }
          },
          "x-amazon-apigateway-integration" : {
            "httpMethod" : "POST",
            "uri" : "arn:aws:apigateway:${data.aws_region.current.name}:lambda:path/2015-03-31/functions/${aws_lambda_function.invocation_function.arn}/invocations",
            "responses" : {
              "default" : {
                "statusCode" : "200"
              }
            },
            "passthroughBehavior" : "when_no_match",
            "contentHandling" : "CONVERT_TO_TEXT",
            "type" : "aws_proxy"
          }
        }
      }
    }
    "components" : {
      "schemas" : {
        "Empty" : {
          "title" : "Empty Schema",
          "type" : "object"
        }
      }
    }
  })

  endpoint_configuration {
    types = [var.endpoint_type]
  }

  tags = var.tags
}

resource "aws_api_gateway_deployment" "deployment" {
  rest_api_id = aws_api_gateway_rest_api.api.id

  triggers = {
    redeployment = sha1(jsonencode(aws_api_gateway_rest_api.api.body))
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_api_gateway_stage" "stage" {
  deployment_id = aws_api_gateway_deployment.deployment.id
  rest_api_id   = aws_api_gateway_rest_api.api.id
  stage_name    = local.stage_name
  tags          = var.tags
}

resource "aws_api_gateway_method_settings" "all" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  stage_name  = aws_api_gateway_stage.stage.stage_name
  method_path = "*/*"

  settings {
    logging_level      = var.log_level
    data_trace_enabled = var.full_debug_mode
    metrics_enabled    = true
  }

  depends_on = [
    aws_cloudwatch_log_group.log_group,
    aws_api_gateway_account.create_apigw_logs_account_role_association
  ]
}

## Associate WAF
resource "aws_wafv2_web_acl_association" "waf_assoc" {
  resource_arn = aws_api_gateway_stage.stage.arn
  web_acl_arn  = var.waf_arn
}

resource "aws_lambda_permission" "api_gateway_permission" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.invocation_function.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.api.execution_arn}/*/*"
}
