# Create log group for lambda logs
resource "aws_cloudwatch_log_group" "backend_func_log_group" {
  name              = "/aws/lambda/${var.backend_lambda_name}"
  retention_in_days = var.lambda_logs_retention
}

# Create Lambda role
resource "aws_iam_role" "backend_func_role" {
  name = "${var.backend_lambda_name}-role"
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
    "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole",
    "arn:aws:iam::aws:policy/AWSOrganizationsReadOnlyAccess",
    "arn:aws:iam::aws:policy/AmazonBedrockReadOnly"
  ]

  inline_policy {
    name = "${var.backend_lambda_name}-role"
    policy = jsonencode({
      Version = "2012-10-17",
      Statement = [
        {
          Sid    = "AllowListSecrets",
          Effect = "Allow",
          Action = [
            "secretsmanager:GetRandomPassword",
            "secretsmanager:ListSecrets",
            "secretsmanager:BatchGetSecretValue"
          ],
          Resource = ["*"]
        },
        {
          Sid    = "AllowReadSecrets",
          Effect = "Allow",
          Action = [
            "secretsmanager:GetResourcePolicy",
            "secretsmanager:GetSecretValue",
            "secretsmanager:DescribeSecret",
            "secretsmanager:ListSecretVersionIds"
          ],
          Resource = var.secrets_arn_list
        },
        {
          Sid      = "AllowAssumeRole",
          Effect   = "Allow",
          Action   = ["sts:AssumeRole"],
          Resource = ["arn:aws:iam::*:role/${var.security_scanner_role_name}"]
        },
        {
          Sid    = "AllowBedrockRead",
          Effect = "Allow",
          Action = [
            "bedrock:ApplyGuardrail",
            "bedrock:DetectGeneratedContent",
            "bedrock:GetAgent",
            "bedrock:GetAgentActionGroup",
            "bedrock:GetAgentAlias",
            "bedrock:GetAgentKnowledgeBase",
            "bedrock:GetAgentVersion",
            "bedrock:GetDataSource",
            "bedrock:GetEvaluationJob",
            "bedrock:GetGuardrail",
            "bedrock:GetIngestionJob",
            "bedrock:GetKnowledgeBase",
            "bedrock:GetModelEvaluationJob",
            "bedrock:GetModelInvocationJob",
            "bedrock:GetUseCaseForModelAccess",
            "bedrock:InvokeAgent",
            "bedrock:InvokeModel",
            "bedrock:InvokeModelWithResponseStream",
            "bedrock:ListAgentActionGroups",
            "bedrock:ListAgentAliases",
            "bedrock:ListAgentKnowledgeBases",
            "bedrock:ListAgents",
            "bedrock:ListAgentVersions",
            "bedrock:ListDataSources",
            "bedrock:ListEvaluationJobs",
            "bedrock:ListFoundationModelAgreementOffers",
            "bedrock:ListGuardrails",
            "bedrock:ListIngestionJobs",
            "bedrock:ListKnowledgeBases",
            "bedrock:ListModelEvaluationJobs",
            "bedrock:ListModelInvocationJobs",
            "bedrock:Retrieve"
          ],
          Resource = ["*"]
        }
      ]
    })
  }
  tags = var.tags
}

data "archive_file" "lambda" {
  type        = "zip"
  source_dir  = "${path.module}/backend"
  output_path = "${path.module}/backend.zip"
}

# Create function
resource "aws_lambda_function" "backend_function" {
  depends_on       = [aws_cloudwatch_log_group.backend_func_log_group]
  function_name    = var.backend_lambda_name
  description      = "Lambda function for ${var.backend_lambda_name}"
  filename         = "${path.module}/backend.zip"
  handler          = "lambda_function.lambda_handler"
  role             = aws_iam_role.backend_func_role.arn
  runtime          = "python3.12"
  timeout          = 180
  architectures    = ["x86_64"]
  source_code_hash = data.archive_file.lambda.output_base64sha256
  tags             = var.tags
  environment {
    variables = {
      DOMAIN                                 = "your-domain.com"
      SECRETS_MANAGER_OKTA_TOKEN_ARN         = "arn:aws:secretsmanager:us-west-2:123456789012:secret:okta-token"
      OKTA_ORGANIZATION_NAME                 = "your-okta-organization-name"
      SECRETS_MANAGER_GITHUB_TOKEN_ARN       = "arn:aws:secretsmanager:us-west-2:123456789012:secret:github-token"
      GITHUB_OWNER                           = "your-github-owner"
      TERRAFORM_ENVIRONMENT_REPOSITORY_NAME  = "your-terraform-environment-repository-name"
      TERRAFORM_MODULE_REPOSITORY_NAME       = "your-terraform-module-repository-name"
      TERRAFORM_ENVIRONMENT_SSO_ACCOUNT_PATH = "/terraform-environments/sso-account"
      TERRAFORM_MODULE_SSO_PATH              = "/terraform-modules/sso"
      SECRETS_MANAGER_PD_TOKEN_ARN           = "arn:aws:secretsmanager:us-west-2:123456789012:secret:pagerduty-token"
      PAGER_DUTY_SCHEDULE_ID                 = "your-pager-duty-schedule-id"
      SECRETS_MANAGER_JIRA_TOKEN_ARN         = "arn:aws:secretsmanager:us-west-2:123456789012:secret:jira-token"
      JIRA_PROJECT_KEY                       = "your-jira-project-key"
      JIRA_ISSUE_TYPE                        = "your-jira-issue-type"
      JIRA_ORGANIZATION_NAME                 = "your-jira-organization-name"
    }
  }
}