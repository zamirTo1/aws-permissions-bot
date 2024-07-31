# Create log group for lambda logs
resource "aws_cloudwatch_log_group" "invocation_func_log_group" {
  name              = "/aws/lambda/${var.invocation_lambda_name}"
  retention_in_days = var.lambda_logs_retention
}

# Create Lambda role
resource "aws_iam_role" "invocation_func_role" {
  name = "${var.invocation_lambda_name}-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Sid    = "LambdaTrustedPolicy"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        },
        Action = "sts:AssumeRole"
      },
    ]
  })

  managed_policy_arns = [
    "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
  ]

  inline_policy {
    name = "${var.invocation_lambda_name}-role"
    policy = jsonencode({
      Version = "2012-10-17",
      Statement = [
        {
          Sid    = "AllowInvokeLambda",
          Effect = "Allow",
          Action = [
            "lambda:InvokeFunction"
          ],
          Resource = [
            aws_lambda_function.backend_function.arn
          ]
        }
      ]
    })
  }
  tags = var.tags
}

data "archive_file" "invocation_lambda" {
  type        = "zip"
  source_dir  = "${path.module}/invocation"
  output_path = "${path.module}/invocation.zip"
}

# Create function
resource "aws_lambda_function" "invocation_function" {
  depends_on       = [aws_cloudwatch_log_group.invocation_func_log_group]
  function_name    = var.invocation_lambda_name
  description      = "Lambda function for ${var.backend_lambda_name}"
  filename         = "${path.module}/invocation.zip"
  handler          = "lambda_function.lambda_handler"
  role             = aws_iam_role.invocation_func_role.arn
  runtime          = "python3.12"
  timeout          = 180
  architectures    = ["x86_64"]
  source_code_hash = data.archive_file.lambda.output_base64sha256
  tags             = var.tags
  environment {
    variables = {
      LAMBDA_NAME = var.backend_lambda_name
    }
  }
}
