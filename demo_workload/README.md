# InfraShift AWS Demonstration Workload

This directory contains the Infrastructure as Code (IaC), Lambda handler, seed data scripts, traffic generator, and deployment tools for the **InfraShift** demonstration workload.

Product Goal: *"Before you deploy the code, know what it could do to your cloud."*

---

## 1. Architecture Diagram

```text
GitHub PR / Code Change (e.g. PR-102)
        ↓
InfraShift Backend API (/api/pr/:id, /api/forecast, /api/test)
        ↓
API Gateway (infraShift-demo-api)
        ↓ GET /users/{id}
Lambda (infraShift-demo-lambda)
        ↓ DynamoDB getItem
DynamoDB (infraShift-demo-users table)
        ↓
CloudWatch Metrics & Logs (Invocations, Duration, ConsumedReadCapacityUnits)
        ↓
InfraShift Telemetry & Forecast Engine
        ↓
Controlled Test Execution & Post-Test Outcome Comparison (/api/outcome/:id)
```

---

## 2. AWS Services Used
1. **AWS API Gateway**: HTTP API Gateway `infraShift-demo-api` exposing `GET /users/{id}`.
2. **AWS Lambda**: Python 3.12 function `infraShift-demo-lambda` performing DynamoDB reads.
3. **AWS DynamoDB**: Pay-per-request table `infraShift-demo-users` (Hash Key: `userId`).
4. **AWS CloudWatch**: Collects `Invocations`, `Duration`, `Errors`, `Throttles`, and log events.
5. **AWS IAM**: Execution roles enforcing least-privilege permissions.

---

## 3. Resource Names
* **API Gateway**: `infraShift-demo-api`
* **Lambda Function**: `infraShift-demo-lambda`
* **DynamoDB Table**: `infraShift-demo-users`
* **Lambda IAM Execution Role**: `InfraShiftDemoLambdaRole`
* **Backend Telemetry IAM Role**: `InfraShiftBackendTelemetryRole`
* **CloudWatch Log Group**: `/aws/lambda/infraShift-demo-lambda`

---

## 4. Required IAM Permissions

### Lambda Execution Role (`InfraShiftDemoLambdaRole`)
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:Query",
        "dynamodb:Scan"
      ],
      "Resource": "arn:aws:dynamodb:*:*:table/infraShift-demo-users"
    },
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "*"
    }
  ]
}
```

### Backend Telemetry Read Role (`InfraShiftBackendTelemetryRole`)
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "cloudwatch:GetMetricData",
        "cloudwatch:GetMetricStatistics",
        "cloudwatch:ListMetrics",
        "logs:FilterLogEvents",
        "logs:GetLogEvents",
        "dynamodb:DescribeTable",
        "lambda:GetFunction"
      ],
      "Resource": "*"
    }
  ]
}
```

---

## 5. Environment Variables

| Variable | Description | Default |
| :--- | :--- | :--- |
| `AWS_REGION` | Target AWS Region | `us-east-1` |
| `LIVE_AWS` | Enables live AWS CloudWatch retrieval | `false` |
| `USE_MOCK_DATA` | Force local mock data telemetry mode | `false` |
| `TABLE_NAME` | Target DynamoDB table name | `infraShift-demo-users` |
| `FUNCTION_NAME` | Target Lambda function name | `infraShift-demo-lambda` |

---

## 6. Deployment Instructions

### Deploy IaC CloudFormation Stack
```bash
python demo_workload/deploy.py
```
This script will:
1. Validate `demo_workload/template.yaml`.
2. Create/Update `infraShift-demo-stack` via boto3 CloudFormation.
3. Package and upload `lambda_function.py`.
4. Execute `seed_data.py` to populate test user items (`user-001`, `user-002`, `user-003`).

---

## 7. Local Development & Mock Mode
When running locally without live AWS credentials:
* Set `LIVE_AWS=false` or `USE_MOCK_DATA=true`.
* The backend API labels telemetry responses with `"source": "MOCK_DATA_LOCAL_DEV"`.
* When credentials are created and connected, telemetry responses indicate `"source": "REAL_AWS_TELEMETRY"`.

---

## 8. Generating Test Traffic
Generate 30 synthetic requests against the workload:
```bash
python demo_workload/generate_traffic.py
```

---

## 9. Running Verification
Execute the 12-point automated verification checklist:
```bash
python verify_aws_workload.py
```
Expected output:
```text
VERIFICATION STATUS: 12/12 POINTS PASSED
```

---

## 10. Controlled Test Workflow
1. Invoke `POST /api/forecast` to generate initial baseline and prediction.
2. Invoke `POST /api/test` to trigger controlled traffic test.
3. Invoke `GET /api/outcome/:id` to retrieve forecast vs actual comparison metrics.

---

## 11. Cleanup Instructions
Delete all deployed AWS resources and stacks:
```bash
python demo_workload/cleanup.py
```
