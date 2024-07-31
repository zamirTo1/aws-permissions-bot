# Deploying CloudFormation Template with AWS CloudFormation StackSets

This guide will assist you in deploying a CloudFormation template using AWS CloudFormation StackSets. 
The StackSet will create a `SecurityAuditRole` in the specified target accounts. This role includes permissions to list and describe resources within the account. 
Additionally, the `SecurityAuditRole` can be assumed by a backend Lambda function located in the security account.


## Prerequisites

- AWS Management Console access
- AWS CLI installed and configured (for CLI method)
- CloudFormation template ready and stored in an accessible location (S3 bucket or local machine)

# Steps to Deploy Using AWS Management Console

## Step 1: Prepare the Template

Ensure your CloudFormation template is ready and stored in an accessible location, such as an S3 bucket or on your local machine.

## Step 2: Create a New StackSet

1. **Sign in to the AWS Management Console** and open the CloudFormation console at [https://console.aws.amazon.com/cloudformation](https://console.aws.amazon.com/cloudformation).

2. In the **CloudFormation console**, choose **StackSets** from the left-hand menu.

3. Click **Create StackSet**.

4. **Specify template**:
   - **Template source**: Choose `Upload a template file` or `Specify an S3 URL`.
   - If you choose to upload, click `Choose file` and upload your CloudFormation template file.
   - If you specify an S3 URL, enter the URL of the template stored in your S3 bucket.

5. Click **Next**.

## Step 3: Configure StackSet Details

1. **StackSet name**: Provide a name for your StackSet.

2. **Parameters**: Enter the parameter values if required by your template. For the `SecurityAccountId`, you can either use the default value specified in the template or override it.

3. Click **Next**.

## Step 4: Set Deployment Options

1. **Deployment targets**: Choose how you want to deploy the StackSet.
   - **Deploy to AWS Organizations**: If you are using AWS Organizations, you can select organizational units (OUs).
   - **Deploy to accounts**: You can specify the AWS account numbers to which you want to deploy the stack.

2. **Regions**: Choose the AWS regions where you want to deploy the StackSet instances.

3. Click **Next**.

## Step 5: Configure StackSet Options

1. **Permission model**: Choose the appropriate permission model.
   - **Service-managed permissions**: Allows AWS CloudFormation to create roles on your behalf in the target accounts.
   - **Self-managed permissions**: You need to manually create IAM roles in the target accounts.

2. **StackSet execution role name**: If you chose self-managed permissions, specify the IAM role that CloudFormation should assume to deploy the stack.

3. **Rate controls**: Optionally, configure the number of accounts in which to deploy stacks concurrently and failure tolerance.

4. Click **Next**.

## Step 6: Review and Create

1. **Review your settings** to ensure everything is correct.

2. Click **Submit** to create the StackSet.
