import boto3
from botocore.exceptions import ClientError
import logging
logger = logging.getLogger()
logger.setLevel("INFO")


class AWSConnector:
    """
    A class used to connect AWS

    ...

    Attributes
    ----------
    aws_accounts : dict
        a dictionary mapping AWS account names to their IDs
    account_id : str
        the ID of the AWS account
    account_ou : str
        the name of the organizational unit that the account belongs to

    Methods
    -------
    __list_organizational_units(parent_id: str, client: boto3.client) -> list:
        Lists the organizational units for a given parent ID
    __find_ou_name_by_account_id() -> str:
        Finds the name of the organizational unit that the account belongs to
    __get_aws_accounts() -> dict:
        Gets a dictionary mapping AWS account names to their IDs
    __assume_role() -> dict:
        Assumes the 'security-scanning' role for the account
    list_s3_buckets() -> list:
        Lists the S3 buckets in the account
    list_sqs_queues() -> list:
        Lists the SQS queues in the account
    aws_bedrock(prompt: str) -> str:
        Uses the Bedrock AI model to generate a response to a prompt
    get_secret_from_secrets_mangers(key: str) -> str:
        Gets a secret from AWS Secrets Manager
    """
    def __init__(self, account_name: str):
        """
        Constructs all the necessary attributes for the AWSConnector.

        Parameters
        ----------
            account_name : str
                the name of the AWS account
        """
        self.aws_accounts = self.__get_aws_accounts()
        self.account_id = self.aws_accounts.get(account_name)
        self.account_ou = self.__find_ou_name_by_account_id()

    @staticmethod
    def __list_organizational_units(parent_id, client):
        """
        Lists the organizational units for a given parent ID.

        Parameters
        ----------
            parent_id : str
                the ID of the parent
            client : boto3.client
                the boto3 client

        Returns
        -------
            list
                a list of organizational units
        """
        ous = []
        paginator = client.get_paginator('list_organizational_units_for_parent')
        response_iterator = paginator.paginate(ParentId=parent_id)

        for response in response_iterator:
            ous.extend(response['OrganizationalUnits'])
        return ous

    def __find_ou_name_by_account_id(self) -> str:
        """
        Finds the name of the organizational unit that the account belongs to.

        Returns
        -------
            str
                the name of the organizational unit
        """
        client = boto3.client('organizations')
        roots = client.list_roots()
        root_id = roots['Roots'][0]['Id']
        queue = [root_id]

        while queue:
            parent_id = queue.pop(0)
            ous = self.__list_organizational_units(parent_id, client)

            for ou in ous:
                queue.append(ou['Id'])
                ou_accounts_paginator = client.get_paginator('list_accounts_for_parent')
                ou_accounts_response_iterator = ou_accounts_paginator.paginate(ParentId=ou['Id'])
                for ou_accounts_response in ou_accounts_response_iterator:
                    for account in ou_accounts_response['Accounts']:
                        if account['Id'] == self.account_id:
                            return ou['Name']
        return ""

    @staticmethod
    def __get_aws_accounts() -> dict:
        """
        Gets a dictionary mapping AWS account names to their IDs.

        Returns
        -------
            dict
                a dictionary mapping AWS account names to their IDs
        """
        client = boto3.client('organizations')
        response = client.list_accounts(
            MaxResults=20
        )
        accounts = {}
        while True:
            aws_accounts = response.get("Accounts")
            next_token = response.get("NextToken")
            if aws_accounts:
                for account in aws_accounts:
                    if account.get("Status") == "ACTIVE":
                        accounts[account.get("Name")] = account.get("Id")
            if next_token:
                response = client.list_accounts(
                    MaxResults=20,
                    NextToken=next_token
                )
            else:
                break
        return accounts

    def __assume_role(self) -> dict:
        """
        Assumes the 'security-scanning' role for the account.

        Returns
        -------
            dict
                the response from the 'AssumeRole' operation
        """
        client = boto3.client('sts')
        try:
            response = client.assume_role(
                RoleArn=f'arn:aws:iam::{self.account_id}:role/security-scanning',
                RoleSessionName='security-scanning-session'
            )
        except ClientError as e:
            logger.error(f"ERROR: AWSHandler.__assume_role: {e}")
            return {}
        return response

    def list_s3_buckets(self) -> list:
        """
        Lists the S3 buckets in the account.

        Returns
        -------
            list
                a list of S3 bucket names
        """
        response = self.__assume_role()
        s3_client = boto3.client(
            's3',
            aws_access_key_id=response.get("Credentials").get("AccessKeyId"),
            aws_secret_access_key=response.get("Credentials").get("SecretAccessKey"),
            aws_session_token=response.get("Credentials").get("SessionToken")
        )
        try:
            account_buckets = s3_client.list_buckets()
        except Exception as e:
            logger.error("AWSHandler.list_s3_buckets: {}".format(e))
            return []
        buckets = []
        for bucket in account_buckets.get("Buckets"):
            buckets.append(bucket.get("Name"))
        return buckets

    def list_sqs_queues(self) -> list:
        """
        Lists the SQS queues in the account.

        Returns
        -------
            list
                a list of SQS queue names
        """
        response = self.__assume_role()
        sqs_client = boto3.client(
            'sqs',
            aws_access_key_id=response.get("Credentials").get("AccessKeyId"),
            aws_secret_access_key=response.get("Credentials").get("SecretAccessKey"),
            aws_session_token=response.get("Credentials").get("SessionToken")
        )
        queues = []
        next_token = None
        while True:
            try:
                if next_token:
                    account_queues = sqs_client.list_queues(
                        MaxResults=1000,
                        NextToken=next_token
                    )
                else:
                    account_queues = sqs_client.list_queues(
                        MaxResults=1000
                    )
            except Exception as e:
                logger.error("AWSHandler.list_sqs_queues: {}".format(e))
                return []
            if "QueueUrls" in account_queues:
                for queue in account_queues.get("QueueUrls"):
                    queues.append(queue.split("/")[-1])

            next_token = account_queues.get("NextToken")
            if not next_token:
                break
        return queues

    @staticmethod
    def aws_bedrock(prompt: str) -> str:
        """
        Uses the Bedrock AI model to generate a response to a prompt.

        Parameters
        ----------
            prompt : str
                the prompt for the AI model

        Returns
        -------
            str
                the response from the AI model
        """
        session = boto3.Session()
        bedrock = session.client('bedrock-runtime', region_name='us-east-1')
        try:
            response = bedrock.converse(
                inferenceConfig={
                    'temperature': 0,
                },
                modelId='anthropic.claude-3-5-sonnet-20240620-v1:0',
                system=[
                    {
                        'text': """
                            You are an AWS IAM and Terraform Expert, you’ll need to use the Terraform module and create a pull request with the change describe in the following prompt.
                            Your boundaries are S3 or SQS permissions only, any other request for permissions will be automatically rejected and you will reply "I'm sorry, I can't do that".
                            YOU WILL REPLY ONLY WITH THE TERRAFORM CODE. 
                            THE CODE MUST BE ERROR-LESS AND FORMATTED. 
                            DO NOT EXPLAIN YOUR ANSWER.
                            DO NOT ADD DECORATIONS OR ANY COMMENTS IN THE CODE.
                            YOU ARE ALLOWED TO CHANGE ONLY THE ENVIRONMENT CODE.
                            IF CUSTOM IAM POLICY DOCUMENT USED ADD IT TO YOUR RESPONSE AS IS.
                        """
                    }
                ],
                messages=[
                    {
                        'role': 'user',
                        'content': [
                            {
                                'text': prompt
                            }
                        ]
                    }
                ]
            )
            result = response['output']['message']['content'][0]['text']
        except Exception as e:
            logger.error("AWSHandler.aws_bedrock: {}".format(e))
            return ""
        return result

    @staticmethod
    def get_secret_from_secrets_mangers(key: str) -> str:
        """
        Gets a secret from AWS Secrets Manager.

        Parameters
        ----------
            key : str
                the name of the secret

        Returns
        -------
            str
                the secret value
        """
        secret_name = key
        region_name = "us-west-2"
        session = boto3.Session()
        client = session.client(
            service_name='secretsmanager',
            region_name=region_name
        )
        try:
            get_secret_value_response = client.get_secret_value(
                SecretId=secret_name
            )
            return get_secret_value_response['SecretString']
        except ClientError as e:
            if e.response['Error']['Code'] == 'DecryptionFailureException':
                # Secrets Manager can't decrypt the protected secret text using the provided KMS key.
                # Deal with the exception here, and/or rethrow at your discretion.
                print("ERROR: AWSHandler.get_secret_from_secrets_mangers: {}".format(e))
            elif e.response['Error']['Code'] == 'InternalServiceErrorException':
                # An error occurred on the server side.
                # Deal with the exception here, and/or rethrow at your discretion.
                print("ERROR: AWSHandler.get_secret_from_secrets_mangers: {}".format(e))
            elif e.response['Error']['Code'] == 'InvalidParameterException':
                # You provided an invalid value for a parameter.
                # Deal with the exception here, and/or rethrow at your discretion.
                print("ERROR: AWSHandler.get_secret_from_secrets_mangers: {}".format(e))
            elif e.response['Error']['Code'] == 'InvalidRequestException':
                # You provided a parameter value that is not valid for the current state of the resource.
                # Deal with the exception here, and/or rethrow at your discretion.
                print("ERROR: AWSHandler.get_secret_from_secrets_mangers: {}".format(e))
            elif e.response['Error']['Code'] == 'ResourceNotFoundException':
                # We can't find the resource that you asked for.
                # Deal with the exception here, and/or rethrow at your discretion.
                print("ERROR: AWSHandler.get_secret_from_secrets_mangers: {}".format(e))
        return ""
