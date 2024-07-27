<div align="center">
<img src="images/img.png" width="500">
</div>

# AWS Permissions Bot - AI-powered self-service bot for AWS permissions

AWS Permissions Bot is an AI-powered self-service tool that automates AWS IAM permissions management. It integrates with Okta for identity management, GitHub for permissions review, PagerDuty for on-call assignment, Jira for issue tracking and task management, and Slack for communication and notifications.

 
## How it works

1. Slack app listens for slash commands.
2. The lambda frontend invoke the backend lambda function and return OK status. 
3. The backend lambda checks for the user's AWS group in Okta. 
4. The backend lambda lists the resources for the requested AWS account.
5. In case of list command, the backend lambda returns the list of resources. 
6. In case of grant command, the backend lambda reads the Terraform sso module and the current Terraform environment. 
7. The backend lambda runs a query towards AWS Bedrock for the requested permissions. 
8. The backend lambda create a GitHub pull request.
9. The backend lambda checks the security on-call personal in PagerDuty.
10. The backend lambda creates a Jira ticket and assign it to the security on-call personal.
11. The backend lambda sends a Slack message to the requester with the Jira ticket link.



## Requirements

- [Slack application](https://api.slack.com/quickstart) with [slash command](https://api.slack.com/interactivity/slash-commands) enabled.
- [Jira token](https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/).
- [PagerDuty API key](https://support.pagerduty.com/docs/generating-api-keys).
- [GitHub personal access token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#creating-a-fine-grained-personal-access-token).
- [Okta Token](https://developer.okta.com/docs/guides/create-an-api-token/main/).
- AWS account with access to Bedrock Claud Sonnet 3.5 and view permissions for organization accounts.



## Runtime 
- Terraform version 1.8.2 
- AWS provider version 5.59.0.



## Installation

1. Connect to AWS account and store the following secrets (Note the secrets ARNs):
   - Okta API token
   - GitHub token
   - PagerDuty API key
   - Jira API token


2. Clone the repository:
   ```
   git clone https://github.com/zamirTo1/aws-permissions-bot.git
   cd aws-permissions-bot
   ```
3. Update the `backend_lambda.tf` environment variables.
   ```
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
   ```

4. Run the following commands:
   ```
   terraform init
   terraform validate
   terraform plan
   terraform apply
   ```
5. From the AWS console navigate to API Gateway -> Stages -> live -> copy the Invoke URL.
6. Create a new Slack slash command with the copied Invoke URL.



## Usage

To use the bot, run on of th following commands in Slack:
```
/aws_permissions list -s s3|sqs -a <account>
/aws_permissions grant -s s3|sqs -p <permission> -a <account> -r <resource> -o <on-behalf> -ps <permission-set-name>
-s, --service: AWS Service
-p, --permission: Permission
-a, --account: AWS Account
-r, --resource: Resource Name
-o, --on-behalf: On Behalf
-ps, --permission-set-name: Permission Set Name
examples:
    /aws_permissions help
    /aws_permissions list -s s3|sqs -a account_name
    /aws_permissions grant -s s3|sqs -p write -a <account_name> -r <bucket_name>
    /aws_permissions grant -s s3|sqs -p write -a <account_name> -r <bucket_name> -o <on-behalf-user-name> -ps <permission-set-name>
```



## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.



## License

This project is licensed under the MIT License. see the [LICENSE](LICENSE) file for details.
