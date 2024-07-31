<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | =1.8.2 |
| <a name="requirement_aws"></a> [aws](#requirement\_aws) | 5.59.0 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_archive"></a> [archive](#provider\_archive) | n/a |
| <a name="provider_aws"></a> [aws](#provider\_aws) | 5.59.0 |

## Modules

No modules.

## Resources

| Name | Type |
|------|------|
| [aws_api_gateway_account.create_apigw_logs_account_role_association](https://registry.terraform.io/providers/hashicorp/aws/5.59.0/docs/resources/api_gateway_account) | resource |
| [aws_api_gateway_deployment.deployment](https://registry.terraform.io/providers/hashicorp/aws/5.59.0/docs/resources/api_gateway_deployment) | resource |
| [aws_api_gateway_method_settings.all](https://registry.terraform.io/providers/hashicorp/aws/5.59.0/docs/resources/api_gateway_method_settings) | resource |
| [aws_api_gateway_rest_api.api](https://registry.terraform.io/providers/hashicorp/aws/5.59.0/docs/resources/api_gateway_rest_api) | resource |
| [aws_api_gateway_stage.stage](https://registry.terraform.io/providers/hashicorp/aws/5.59.0/docs/resources/api_gateway_stage) | resource |
| [aws_cloudwatch_log_group.backend_func_log_group](https://registry.terraform.io/providers/hashicorp/aws/5.59.0/docs/resources/cloudwatch_log_group) | resource |
| [aws_cloudwatch_log_group.invocation_func_log_group](https://registry.terraform.io/providers/hashicorp/aws/5.59.0/docs/resources/cloudwatch_log_group) | resource |
| [aws_cloudwatch_log_group.log_group](https://registry.terraform.io/providers/hashicorp/aws/5.59.0/docs/resources/cloudwatch_log_group) | resource |
| [aws_iam_role.apigw_logs_account_role](https://registry.terraform.io/providers/hashicorp/aws/5.59.0/docs/resources/iam_role) | resource |
| [aws_iam_role.backend_func_role](https://registry.terraform.io/providers/hashicorp/aws/5.59.0/docs/resources/iam_role) | resource |
| [aws_iam_role.invocation_func_role](https://registry.terraform.io/providers/hashicorp/aws/5.59.0/docs/resources/iam_role) | resource |
| [aws_lambda_function.backend_function](https://registry.terraform.io/providers/hashicorp/aws/5.59.0/docs/resources/lambda_function) | resource |
| [aws_lambda_function.invocation_function](https://registry.terraform.io/providers/hashicorp/aws/5.59.0/docs/resources/lambda_function) | resource |
| [aws_lambda_permission.api_gateway_permission](https://registry.terraform.io/providers/hashicorp/aws/5.59.0/docs/resources/lambda_permission) | resource |
| [aws_wafv2_web_acl_association.waf_assoc](https://registry.terraform.io/providers/hashicorp/aws/5.59.0/docs/resources/wafv2_web_acl_association) | resource |
| [archive_file.invocation_lambda](https://registry.terraform.io/providers/hashicorp/archive/latest/docs/data-sources/file) | data source |
| [archive_file.lambda](https://registry.terraform.io/providers/hashicorp/archive/latest/docs/data-sources/file) | data source |
| [aws_caller_identity.current](https://registry.terraform.io/providers/hashicorp/aws/5.59.0/docs/data-sources/caller_identity) | data source |
| [aws_region.current](https://registry.terraform.io/providers/hashicorp/aws/5.59.0/docs/data-sources/region) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_api_gateway_name"></a> [api\_gateway\_name](#input\_api\_gateway\_name) | The name of the API Gateway | `string` | `"aws-permissions-bot"` | no |
| <a name="input_api_path"></a> [api\_path](#input\_api\_path) | The path on the API Gateway where the POST request is accepted and routed to the SQS queue. | `string` | `"/api/user-interaction"` | no |
| <a name="input_backend_lambda_name"></a> [backend\_lambda\_name](#input\_backend\_lambda\_name) | The name of the backend Lambda function | `string` | `"aws-permissions-bot-backend"` | no |
| <a name="input_create_apigw_logs_account_role"></a> [create\_apigw\_logs\_account\_role](#input\_create\_apigw\_logs\_account\_role) | Determines whether to create an IAM role at the account level that allows API Gateway to write logs. Generally, this should be created once per AWS account. | `bool` | `false` | no |
| <a name="input_endpoint_type"></a> [endpoint\_type](#input\_endpoint\_type) | Type of the endpoint for the REST API. Valid values: EDGE or REGIONAL. If unspecified, defaults to EDGE. | `string` | `"REGIONAL"` | no |
| <a name="input_execution_logs_retention"></a> [execution\_logs\_retention](#input\_execution\_logs\_retention) | The number of days to retain the log events in the specified log group. Possible values are: 1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365, 400, 545, 731, 1096, 1827, 2192, 2557, 2922, 3288, 3653, and 0. If you select 0, the events in the log group are always retained and never expire. | `number` | `90` | no |
| <a name="input_full_debug_mode"></a> [full\_debug\_mode](#input\_full\_debug\_mode) | Enables detailed logging for all events in API Gateway. This may include sensitive data, so use with caution. Useful for troubleshooting purposes. | `bool` | `false` | no |
| <a name="input_invocation_lambda_name"></a> [invocation\_lambda\_name](#input\_invocation\_lambda\_name) | The name of the invocation Lambda function | `string` | `"aws-permissions-bot-invocation"` | no |
| <a name="input_lambda_logs_retention"></a> [lambda\_logs\_retention](#input\_lambda\_logs\_retention) | The number of days to retain the log events in the specified log group. Possible values are: 1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365, 400, 545, 731, 1096, 1827, 2192, 2557, 2922, 3288, 3653, and 0. If you select 0, the events in the log group are always retained and never expire. | `number` | `90` | no |
| <a name="input_log_level"></a> [log\_level](#input\_log\_level) | The logging level for the API Gateway. Valid values: OFF, ERROR or INFO. If unspecified, defaults to INFO. | `string` | `"INFO"` | no |
| <a name="input_secrets_arn_list"></a> [secrets\_arn\_list](#input\_secrets\_arn\_list) | A list of ARNs (Amazon Resource Names) of the AWS Secrets Manager secrets that the Lambda function will use to access sensitive data. | `list(string)` | n/a | yes |
| <a name="input_security_scanner_role_name"></a> [security\_scanner\_role\_name](#input\_security\_scanner\_role\_name) | The name of the IAM role that the security scanner Lambda function will assume to list account resources. | `string` | `"SecurityAuditRole"` | no |
| <a name="input_tags"></a> [tags](#input\_tags) | A map of key-value pairs to assign as metadata tags to all resources created by the Terraform script. Useful for cost tracking, ownership identification, etc. | `map(string)` | <pre>{<br>  "managed_by": "terraform",<br>  "project_name": "aws-permissions-bot"<br>}</pre> | no |
| <a name="input_waf_arn"></a> [waf\_arn](#input\_waf\_arn) | The ARN (Amazon Resource Name) of the AWS WAF (Web Application Firewall) to associate with the API Gateway. | `string` | n/a | yes |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_api_id"></a> [api\_id](#output\_api\_id) | The ID of the API Gateway. |
| <a name="output_log_group_name"></a> [log\_group\_name](#output\_log\_group\_name) | The name of the CloudWatch Log Group associated with the API Gateway. |
<!-- END_TF_DOCS -->