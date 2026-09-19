"""
Automated Cleanup Script for InfraShift Demo Workload.
Deletes CloudFormation stack 'infraShift-demo-stack' and cleans up local artifacts.
"""

import os
import boto3
from botocore.exceptions import ClientError

STACK_NAME = os.getenv("STACK_NAME", "infraShift-demo-stack")
REGION = os.getenv("AWS_REGION", "us-east-1")
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def cleanup_stack():
    """Delete CloudFormation stack."""
    print(f"=== InfraShift Demo Workload Cleanup ===")
    print(f"Deleting Stack: {STACK_NAME} in region: {REGION}")

    cf_client = boto3.client("cloudformation", region_name=REGION)

    try:
        cf_client.delete_stack(StackName=STACK_NAME)
        print(f"[+] Stack deletion initiated for '{STACK_NAME}'. Waiting for DELETE_COMPLETE...")
        waiter = cf_client.get_waiter("stack_delete_complete")
        waiter.wait(StackName=STACK_NAME)
        print(f"[+] Stack '{STACK_NAME}' deleted successfully.")

    except ClientError as e:
        print(f"[-] Error deleting stack: {e}")

    # Remove local zip archive if present
    zip_path = os.path.join(SCRIPT_DIR, "lambda.zip")
    if os.path.exists(zip_path):
        os.remove(zip_path)
        print(f"[+] Removed local deployment archive: {zip_path}")


if __name__ == "__main__":
    cleanup_stack()
