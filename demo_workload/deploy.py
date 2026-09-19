"""
Automated Deployment Script for InfraShift Demo Workload.
Deploys CloudFormation stack 'infraShift-demo-stack' and seeds DynamoDB.
"""

import os
import sys
import time
import zipfile
import boto3
from botocore.exceptions import ClientError

STACK_NAME = os.getenv("STACK_NAME", "infraShift-demo-stack")
REGION = os.getenv("AWS_REGION", "us-east-1")
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def create_lambda_zip() -> str:
    """Create deployment zip containing lambda_function.py."""
    zip_path = os.path.join(SCRIPT_DIR, "lambda.zip")
    lambda_src = os.path.join(SCRIPT_DIR, "lambda_function.py")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(lambda_src, arcname="lambda_function.py")
    print(f"[+] Created Lambda deployment archive: {zip_path}")
    return zip_path


def deploy_stack():
    """Deploy CloudFormation stack and seed data."""
    print(f"=== InfraShift Demo Workload Deployment ===")
    print(f"Stack Name: {STACK_NAME}")
    print(f"Region:     {REGION}")

    cf_client = boto3.client("cloudformation", region_name=REGION)
    template_path = os.path.join(SCRIPT_DIR, "template.yaml")

    with open(template_path, "r", encoding="utf-8") as f:
        template_body = f.read()

    print("[+] Validating CloudFormation template...")
    try:
        cf_client.validate_template(TemplateBody=template_body)
        print("[+] Template validation passed.")
    except ClientError as e:
        print(f"[-] CloudFormation validation failed: {e}")
        sys.exit(1)

    print(f"[+] Deploying stack '{STACK_NAME}' via boto3...")
    try:
        cf_client.create_stack(
            StackName=STACK_NAME,
            TemplateBody=template_body,
            Capabilities=["CAPABILITY_IAM", "CAPABILITY_NAMED_IAM", "CAPABILITY_AUTO_EXPAND"],
            Tags=[
                {"Key": "Project", "Value": "InfraShift"},
                {"Key": "Environment", "Value": "Demo"},
            ],
        )
        print("[+] Stack creation initiated. Waiting for CREATE_COMPLETE...")
        waiter = cf_client.get_waiter("stack_create_complete")
        waiter.wait(StackName=STACK_NAME)
        print("[+] Stack deployment complete!")

    except ClientError as e:
        if "AlreadyExistsException" in str(e):
            print(f"[!] Stack '{STACK_NAME}' already exists. Updating stack...")
            try:
                cf_client.update_stack(
                    StackName=STACK_NAME,
                    TemplateBody=template_body,
                    Capabilities=["CAPABILITY_IAM", "CAPABILITY_NAMED_IAM", "CAPABILITY_AUTO_EXPAND"],
                )
                waiter = cf_client.get_waiter("stack_update_complete")
                waiter.wait(StackName=STACK_NAME)
                print("[+] Stack update complete!")
            except ClientError as update_err:
                if "No updates are to be performed" in str(update_err):
                    print("[=] Stack is already up to date.")
                else:
                    print(f"[-] Stack update failed: {update_err}")
                    sys.exit(1)
        else:
            print(f"[-] Stack creation failed: {e}")
            sys.exit(1)

    # 3. Upload Lambda Code
    zip_path = create_lambda_zip()
    lambda_client = boto3.client("lambda", region_name=REGION)
    function_name = "infraShift-demo-lambda"

    with open(zip_path, "rb") as f:
        zip_bytes = f.read()

    try:
        lambda_client.update_function_code(
            FunctionName=function_name,
            ZipFile=zip_bytes,
        )
        print(f"[+] Lambda function code updated for '{function_name}'")
    except ClientError as e:
        print(f"[-] Failed to update Lambda code: {e}")

    # 4. Seed DynamoDB Data
    from seed_data import seed_demo_users
    seed_demo_users(region=REGION)

    # 5. Output Resource Summary
    outputs = cf_client.describe_stacks(StackName=STACK_NAME)["Stacks"][0].get("Outputs", [])
    print("\n=== DEPLOYMENT OUTPUTS ===")
    for out in outputs:
        print(f"{out['OutputKey']}: {out['OutputValue']}")


if __name__ == "__main__":
    deploy_stack()
