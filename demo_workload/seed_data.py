"""
Seed Data Generator for InfraShift Demo Workload.
Populates 'infraShift-demo-users' DynamoDB table with initial demo user records.
"""

import os
import boto3
from botocore.exceptions import ClientError

TABLE_NAME = os.getenv("TABLE_NAME", "infraShift-demo-users")
REGION = os.getenv("AWS_REGION", "us-east-1")

SEED_USERS = [
    {
        "userId": "user-001",
        "name": "Alex Mercer",
        "email": "alex.mercer@infrashift.io",
        "role": "Platform Engineer",
        "tier": "enterprise",
        "createdAt": "2026-09-01T10:00:00Z",
    },
    {
        "userId": "user-002",
        "name": "Sarah Connor",
        "email": "sarah.connor@infrashift.io",
        "role": "DevOps Architect",
        "tier": "pro",
        "createdAt": "2026-09-05T14:30:00Z",
    },
    {
        "userId": "user-003",
        "name": "David Chen",
        "email": "david.chen@infrashift.io",
        "role": "Infrastructure Engineer",
        "tier": "free",
        "createdAt": "2026-09-10T09:15:00Z",
    },
]


def seed_demo_users(table_name: str = TABLE_NAME, region: str = REGION) -> bool:
    """Populate DynamoDB table with seed users."""
    from botocore.exceptions import NoCredentialsError, NoRegionError

    print(f"Connecting to DynamoDB table '{table_name}' in region '{region}'...")
    try:
        dynamodb = boto3.resource("dynamodb", region_name=region)
    except (NoCredentialsError, NoRegionError) as e:
        print(f"[-] AWS CLI Error: Unable to locate credentials or region. Please run 'aws configure' first.")
        print(f"    Details: {e}")
        return False
        
    try:
        table = dynamodb.Table(table_name)

        for user in SEED_USERS:
            table.put_item(Item=user)
            print(f"  [+] Seeded user: {user['userId']} ({user['name']})")

        print("Seed data population completed successfully.")
        return True

    except ClientError as e:
        print(f"[-] Error seeding DynamoDB data: {e.response['Error']['Message']}")
        return False
    except Exception as e:
        print(f"[-] Unexpected error during seeding: {e}")
        return False


if __name__ == "__main__":
    seed_demo_users()
