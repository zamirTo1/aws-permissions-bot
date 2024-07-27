import argparse
import base64
import AWSHandler
import OktaHandler
import GithubHandler
import JiraHandler
import PagerDutyHandler
import SlackHandler
import logging
import os
import json
logger = logging.getLogger()
logger.setLevel("INFO")


def lambda_handler(event, context):
    # Get environment variables
    domain = os.getenv("DOMAIN")
    okta_token_secret_arn = os.getenv("SECRETS_MANAGER_OKTA_TOKEN_ARN")
    okta_organization_name = os.getenv("OKTA_ORGANIZATION_NAME")
    github_token_secret_arn = os.getenv("SECRETS_MANAGER_GITHUB_TOKEN_ARN")
    github_owner = os.getenv("GITHUB_OWNER")
    github_terraform_environment_repository_name = os.getenv("TERRAFORM_ENVIRONMENT_REPOSITORY_NAME")
    github_terraform_module_repository_name = os.getenv("TERRAFORM_MODULE_REPOSITORY_NAME")
    github_terraform_environment_sso_account_path = os.getenv("TERRAFORM_ENVIRONMENT_SSO_ACCOUNT_PATH")
    github_terraform_module_sso_path = os.getenv("TERRAFORM_MODULE_SSO_PATH")
    pager_duty_token_secret_arn = os.getenv("SECRETS_MANAGER_PD_TOKEN_ARN")
    pager_duty_schedule_id = os.getenv("PAGER_DUTY_SCHEDULE_ID")
    jira_token_secret_arn = os.getenv("SECRETS_MANAGER_JIRA_TOKEN_ARN")
    jira_project_key = os.getenv("JIRA_PROJECT_KEY")
    jira_issue_type = os.getenv("JIRA_ISSUE_TYPE")
    jira_organization_name = os.getenv("JIRA_ORGANIZATION_NAME")

    slack_payload = event.get("body")
    okta_group = ""

    # Extract Slack response URL, command, and username
    response_url = SlackHandler.parse_slack_url(slack_payload).get("response_url")[0]
    command = SlackHandler.parse_slack_url(slack_payload).get("text")[0]
    user_name = SlackHandler.parse_slack_url(slack_payload).get("user_name")[0]

    # Parser settings
    parser = argparse.ArgumentParser(add_help=True, description="AWS Permissions Parser")
    subparsers = parser.add_subparsers(dest='command', required=True)

    # Grant Permissions
    grant_parser = subparsers.add_parser("grant", help="Grant Permissions")
    grant_parser.add_argument("-s", "--service", help="AWS Service", required=True)
    grant_parser.add_argument("-p", "--permission", help="Permission", required=True)
    grant_parser.add_argument("-a", "--account", help="AWS Account", required=True)
    grant_parser.add_argument("-r", "--resource", help="Resource Name", required=True)
    grant_parser.add_argument("-o", "--on-behalf", help="On Behalf", required=False)
    grant_parser.add_argument("-ps", "--permission-set-name", help="Permission Set Name", required=False)

    # List Resources
    list_parser = subparsers.add_parser("list", help="List Permissions")
    list_parser.add_argument("-s", "--service", help="AWS Service", required=True)
    list_parser.add_argument("-a", "--account", help="AWS Account", required=True)

    # Help
    subparsers.add_parser("help", help="Help")
    args = parser.parse_args(command.split(" "))

    # Help command - return help message
    if args.command == "help":
        logger.info("Username: {} - asked Help".format(user_name))
        SlackHandler.response_to_slack(
            response_url,
            """```
            /aws_permissions list -s s3|sqs -a <account>\n
            /aws_permissions grant -s s3|sqs -p <permission> -a <account> -r <resource> -o <on-behalf> -ps <permission-set-name>\n
            -s, --service: AWS Service\n
            -p, --permission: Permission\n
            -a, --account: AWS Account\n
            -r, --resource: Resource Name\n
            -o, --on-behalf: On Behalf\n
            -ps, --permission-set-name: Permission Set Name\n
            examples:\n\t
                /aws_permissions list -s s3|sqs -a account_name\n\t
                /aws_permissions grant -s s3|sqs -p write -a <account_name> -r <bucket_name>\n\t
                /aws_permissions grant -s s3|sqs -p write -a <account_name> -r <bucket_name> -o <on-behalf-user-name> -ps <permission-set-name>
            ```""")
        return {"statusCode": 200}

    logger.info("User Name: {}".format(user_name))
    logger.info("Command: {}".format(command))
    logger.info("Service: {}".format(args.service))
    logger.info("Account: {}".format(args.account))
    logger.info("Resource: {}".format(args.resource))
    logger.info("On-Behalf: {}".format(args.on_behalf))
    logger.info("Permission: {}".format(args.permission))
    logger.info("Permission Set Name: {}".format(args.permission_set_name))

    aws_connector = AWSHandler.AWSConnector(args.account)
    if aws_connector.account_id is None:
        logger.error("Account not found")
        SlackHandler.response_to_slack(
            response_url,
            "AWS Permissions bot Error - Account Not found"
        )
        return {"statusCode": 200}

    logger.info("Account ID: {}".format(aws_connector.account_id))

    # Get secrets from AWS Secrets Manager
    okta_token = aws_connector.get_secret_from_secrets_mangers(key=okta_token_secret_arn)
    github_token = aws_connector.get_secret_from_secrets_mangers(key=github_token_secret_arn)
    pager_duty_token = aws_connector.get_secret_from_secrets_mangers(key=pager_duty_token_secret_arn)
    jira_credentials = aws_connector.get_secret_from_secrets_mangers(key=jira_token_secret_arn)

    if not(okta_token and github_token and pager_duty_token and jira_credentials):
        logger.error("Failed to read secrets, please contact the security team")
        SlackHandler.response_to_slack(
            response_url,
            "AWS Permissions bot Error - Failed to read secrets, please contact the security team"
        )
        return {"statusCode": 200}

    if args.on_behalf:
        user_name = args.on_behalf

    logger.info("User Name: {}".format(user_name))

    # Okta get user's groups
    okta_connector = OktaHandler.OktaConnector(token=okta_token, organization_name=okta_organization_name)
    aws_groups = okta_connector.get_user_aws_groups(email_address="{}@{}".format(user_name, domain))

    # Check if user is allowed to perform queries to AWS
    # if the user assigned to multiple groups, ask for permission set
    # if the user assigned to one group, use it
    # if the user not assigned to any group, return error
    if aws_groups is not None:
        if len(aws_groups) > 1 and args.permission_set_name is None:
            logger.error("Multiple permission sets found, please specify a permission set")
            SlackHandler.response_to_slack(
                response_url,
                "AWS Permissions bot Error - Multiple permission sets found, please specify a permission set name"
            )
            return {"statusCode": 200}
        elif len(aws_groups) > 1 and args.permission_set_name is not None:
            for group in aws_groups:
                if set(group.split("_")).intersection(set(args.permission_set_name.split("_"))):
                    okta_group = group
        elif len(aws_groups) == 0:
            logger.error("User not allowed to perform queries to AWS")
            SlackHandler.response_to_slack(
                response_url,
                "AWS Permissions bot Error - User not allowed to perform queries to AWS"
            )
            return {"statusCode": 200}
        else:
            okta_group = aws_groups[0].replace("aws_", "")

    logger.info("Okta Group: {}".format(okta_group))

    if args.service == "s3":
        resources = aws_connector.list_s3_buckets()
    elif args.service == "sqs":
        resources = aws_connector.list_sqs_queues()
    else:
        logger.error("Cannot list for the requested service, please reach out to the security team for more information")
        SlackHandler.response_to_slack(
            response_url,
            "AWS Permissions bot Error - Cannot list for the requested service, please reach out to the security team for more information"
        )
        return {"statusCode": 200}

    # List command - return list of resources
    if args.command == "list":
        resource_string = ""
        for resource in resources:
            resource_string += resource + "\n"
        logger.info(resources)
        SlackHandler.response_to_slack(response_url, "Resources:\n```{}```".format(resource_string))
        return {"statusCode": 200}

    # Grant command - create a Jira ticket and a GitHub pull request
    if args.command == "grant":
        if args.resource not in resources:
            logger.error("Resource not found within the requested account")
            SlackHandler.response_to_slack(
                response_url,
                "AWS Permissions bot Error - Resource not found within the requested account"
            )
            return {"statusCode": 200}

        # GitHub get user permissions for the requested account ID
        github_connector = GithubHandler.GithubConnector(
            token=github_token,
            owner=github_owner,
            terraform_environment_repository_name=github_terraform_environment_repository_name,
            terraform_module_repository_name=github_terraform_module_repository_name,
            terraform_environment_sso_account_path=github_terraform_environment_sso_account_path
        )

        # Read the environment file for the requested account
        environment_file = github_connector.read_file_content(
            repository_name=github_terraform_environment_repository_name,
            file_path="{}/{}/{}.tf".format(github_terraform_environment_sso_account_path, okta_group, args.account)
        )
        environment_file_content = environment_file[0]
        if not environment_file_content:
            logger.error("Account not found in the requested group, please contact the security team for more information")
            SlackHandler.response_to_slack(
                response_url,
                "AWS Permissions bot Error - No permissions set found, please contact the security team for more information")
            return {"statusCode": 200}

        # Read the module files for the requested service
        module_data_file_content = github_connector.read_file_content(
            repository_name=github_terraform_module_repository_name,
            file_path="{}/data.tf".format(github_terraform_module_sso_path)
        )[0]
        module_data_main_content = github_connector.read_file_content(
            repository_name=github_terraform_module_repository_name,
            file_path="{}/main.tf".format(github_terraform_module_sso_path)
        )[0]
        module_data_variables_content = github_connector.read_file_content(
            repository_name=github_terraform_module_repository_name,
            file_path="{}/variables.tf".format(github_terraform_module_sso_path)
        )[0]
        if not (module_data_file_content and module_data_main_content and module_data_variables_content):
            logger.error("Module files not found, please contact the security team for more information")
            SlackHandler.response_to_slack(
                response_url,
                "AWS Permissions bot Error - Module files not found, please contact the security team for more information")
            return {"statusCode": 200}

        # Get Bedrock response
        aws_bedrock_prompt = """
            Add the {} resource named "{}" located in "{}" organization path
            Terraform module:
            {}
            {}
            {}
            Terraform environment file:
            {}
        """.format(
            args.service,
            args.resource,
            aws_connector.account_ou,
            base64.b64decode(module_data_variables_content).decode("utf-8"),
            base64.b64decode(module_data_file_content).decode("utf-8"),
            base64.b64decode(module_data_main_content).decode("utf-8"),
            base64.b64decode(environment_file_content).decode("utf-8")
        )
        aws_bedrock_response = aws_connector.aws_bedrock(prompt=aws_bedrock_prompt)
        # Create a GitHub pull request
        github_pull_request_url = github_connector.create_full_request(
            group_name=okta_group,
            account_name=args.account,
            new_content=aws_bedrock_response,
            service_name=args.service,
            user_name=user_name,
            permission=args.permission,
            resource_name=args.resource
        )
        if github_pull_request_url:
            logger.info("GitHub Pull Request - {} - created successfully".format(github_pull_request_url))
        else:
            logger.error("Github pull request was not created")
            SlackHandler.response_to_slack(
                response_url,
                "AWS Permissions bot Error - Github pull request was not created, please contact the security team"
            )
            return {"statusCode": 200}
        pagerduty_connector = PagerDutyHandler.PagerDutyConnector(token=pager_duty_token)
        security_on_call_email_address = pagerduty_connector.get_on_call_email_address(
            schedule_ids=pager_duty_schedule_id
        )
        if not security_on_call_email_address:
            logger.error("PagerDuty security on call was not found")
            SlackHandler.response_to_slack(
                response_url,
                "AWS Permissions bot Error - Security on call email address was not found, please contact the security team"
            )
            return {"statusCode": 200}

        # Jira create a new issue
        jira_connector = JiraHandler.JiraConnector(
            user=json.loads(jira_credentials).get("username"),
            token=json.loads(jira_credentials).get("token"),
            jira_organization_name=jira_organization_name
        )

        assignee_id = jira_connector.get_user_id_by_email_address(email_address=security_on_call_email_address)
        if assignee_id:
            logger.info("Assignee ID: {}".format(assignee_id))
        else:
            logger.error("Assignee ID was not found")
            SlackHandler.response_to_slack(
                response_url,
                "AWS Permissions bot Error - Assignee ID was not found, please contact the security team")
            return {"statusCode": 200}
        requester_id = jira_connector.get_user_id_by_email_address(
            email_address="{}@{}".format(user_name, domain)
        )
        if requester_id:
            logger.info("Requester Email Address: {}@{}".format(user_name, domain))
            logger.info("Requester ID: {}".format(requester_id))
        else:
            logger.error("Requester ID was not found")
            SlackHandler.response_to_slack(
                response_url,
                "AWS Permissions bot Error - Requester ID was not found, please contact the security team")
            return {"statusCode": 200}

        # Create a Jira ticket
        jira_payload = JiraHandler.JiraConnector.build_jira_ticket(
            project_key=jira_project_key,
            issue_type=jira_issue_type,
            assignee_id=assignee_id,
            assignee_mention=requester_id,
            service_name=args.service,
            resource_name=args.resource,
            permission_level=args.permission,
            account_name=args.account,
            github_pull_request_url=github_pull_request_url
        )
        jira_issue_key = jira_connector.create_new_issue(payload=jira_payload)
        if jira_issue_key:
            logger.info("Jira task - {} - created successfully".format(jira_issue_key))
            SlackHandler.response_to_slack(
                response_url,
                "AWS Permissions bot - Jira ticket {} was created, pull request was generated {}".format(jira_issue_key, github_pull_request_url))
            return {"statusCode": 200}
        else:
            logger.error("Jira task was not created")
            SlackHandler.response_to_slack(
                response_url,
                "AWS Permissions bot Error - Jira task was not created, please contact the security team"
            )
            return {"statusCode": 200}
