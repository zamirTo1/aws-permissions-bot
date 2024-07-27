import boto3
import json
import os


def lambda_handler(event, context):
    client = boto3.client('lambda')
    lambda_name = os.getenv('LAMBDA_NAME')
    client.invoke(
        FunctionName=lambda_name,
        InvocationType='Event',
        Payload=json.dumps(event)
    )
    return {
        'statusCode': 200
    }
