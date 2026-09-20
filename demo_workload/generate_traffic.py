"""
Traffic Generation Script for InfraShift Demo Workload.
Generates synthetic traffic against API Gateway / Lambda to produce real CloudWatch telemetry.
"""

import json
import os
import time
import urllib.request
import urllib.error
import boto3

REGION = os.getenv("AWS_REGION", "us-east-1")
FUNCTION_NAME = os.getenv("FUNCTION_NAME", "infraShift-demo-lambda")


def generate_traffic(requests_count: int = 25, delay_seconds: float = 0.2, api_url: str = None):
    """
    Generate real workload execution traffic to populate CloudWatch metrics.

    :param requests_count: Number of requests to generate.
    :param delay_seconds: Delay between requests in seconds.
    :param api_url: Optional HTTP API Gateway base URL.
    """
    print(f"=== InfraShift Demo Workload Traffic Generator ===")
    print(f"Targeting: {api_url or FUNCTION_NAME}")
    print(f"Requests Count: {requests_count}")

    from botocore.exceptions import NoCredentialsError, NoRegionError
    
    try:
        lambda_client = boto3.client("lambda", region_name=REGION) if not api_url else None
    except (NoCredentialsError, NoRegionError) as e:
        print(f"[-] AWS CLI Error: Unable to locate credentials or region. Please run 'aws configure' first.")
        print(f"    Details: {e}")
        import sys
        sys.exit(1)

    successes = 0
    not_founds = 0
    errors = 0

    for i in range(requests_count):
        target_id = user_ids[i % len(user_ids)]

        if api_url:
            # Send HTTP GET via API Gateway
            url = f"{api_url.rstrip('/')}/users/{target_id}"
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "InfraShift-TrafficGen/1.0"})
                with urllib.request.urlopen(req) as resp:
                    code = resp.getcode()
                    if code == 200:
                        successes += 1
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    not_founds += 1
                else:
                    errors += 1
            except Exception:
                errors += 1
        else:
            # Direct Lambda invocation via boto3
            payload = json.dumps({"pathParameters": {"id": target_id}, "userId": target_id})
            try:
                response = lambda_client.invoke(
                    FunctionName=FUNCTION_NAME,
                    InvocationType="RequestResponse",
                    Payload=payload.encode("utf-8"),
                )
                res_payload = json.loads(response["Payload"].read().decode("utf-8"))
                status = res_payload.get("statusCode", 500)
                if status == 200:
                    successes += 1
                elif status == 404:
                    not_founds += 1
                else:
                    errors += 1
            except Exception as e:
                print(f"[-] Invocation error: {e}")
                errors += 1

        if (i + 1) % 5 == 0 or (i + 1) == requests_count:
            print(f"  [+] Sent {i + 1}/{requests_count} requests | Success: {successes} | 404: {not_founds} | Errors: {errors}")

        time.sleep(delay_seconds)

    print("\n=== TRAFFIC GENERATION COMPLETE ===")
    print(f"Total Requests: {requests_count}")
    print(f"200 OK:         {successes}")
    print(f"404 Not Found:  {not_founds}")
    print(f"Errors:         {errors}")
    print("CloudWatch metrics will be populated within 1-3 minutes.")


if __name__ == "__main__":
    generate_traffic(requests_count=30, delay_seconds=0.1)
