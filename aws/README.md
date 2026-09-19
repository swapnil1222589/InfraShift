# InfraShift — AWS Infrastructure & Evidence Layer

This module provides real AWS resource discovery, CloudWatch telemetry collection, normalized resource & dependency models, X-Ray trace evidence extraction, and safe AWS configuration management for the **InfraShift** infrastructure impact predictor.

---

## Architecture Overview

```
aws/
├── config/             # Safe boto3 session factory & AWS credential management
│   ├── __init__.py
│   └── aws_config.py
├── models/             # Pydantic v2 schemas for normalized resources, dependencies, & telemetry
│   ├── __init__.py
│   └── aws_models.py
├── discovery/          # Discovery for API Gateway, Lambda, DynamoDB & Dependency Graph
│   ├── __init__.py
│   ├── resource_discovery.py
│   ├── lambda_discovery.py
│   ├── dynamodb_discovery.py
│   ├── api_gateway_discovery.py
│   └── dependency_discovery.py # Unified dependency orchestrator
├── telemetry/          # Reusable CloudWatch metric collectors (empty datapoint safe)
│   ├── __init__.py
│   ├── cloudwatch.py
│   └── metrics.py
├── tracing/            # X-Ray trace metadata & segment evidence parser
│   ├── __init__.py
│   └── xray.py
├── tests/              # Unit tests with 100% mocked AWS SDK calls
└── README.md
```

---

## 1. Local AWS Configuration

InfraShift relies on `boto3` and the standard AWS Credential Provider Chain. **Never commit AWS credentials or secrets to source code.**

### Option A: AWS CLI Profile (Recommended for local development)
Configure your profile using `aws configure`:
```bash
aws configure --profile infrashift-dev
```
Then set `AWS_PROFILE` in your environment or `.env` file:
```env
AWS_PROFILE=infrashift-dev
AWS_REGION=ap-south-1
```

### Option B: Environment Variables
```env
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=us-east-1
```

---

## 2. AWS Region Configuration

Region resolution priority:
1. Explicit parameter passed to `AWSConfig(region_name="...")`
2. `AWS_REGION` environment variable
3. `AWS_DEFAULT_REGION` environment variable
4. Configured region in active AWS CLI profile (`AWS_PROFILE`)
5. Default fallback: `us-east-1`

---

## 3. Required IAM Permissions

The InfraShift AWS layer requires **read-only** IAM permissions to discover resources, collect CloudWatch metrics, and query X-Ray trace evidence:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "InfraShiftLambdaDiscovery",
      "Effect": "Allow",
      "Action": [
        "lambda:ListFunctions",
        "lambda:GetFunction",
        "lambda:GetFunctionConfiguration"
      ],
      "Resource": "*"
    },
    {
      "Sid": "InfraShiftDynamoDBDiscovery",
      "Effect": "Allow",
      "Action": [
        "dynamodb:ListTables",
        "dynamodb:DescribeTable"
      ],
      "Resource": "*"
    },
    {
      "Sid": "InfraShiftAPIGatewayDiscovery",
      "Effect": "Allow",
      "Action": [
        "apigateway:GET"
      ],
      "Resource": "*"
    },
    {
      "Sid": "InfraShiftCloudWatchTelemetry",
      "Effect": "Allow",
      "Action": [
        "cloudwatch:GetMetricStatistics"
      ],
      "Resource": "*"
    },
    {
      "Sid": "InfraShiftXRayTracingEvidence",
      "Effect": "Allow",
      "Action": [
        "xray:GetServiceGraph",
        "xray:GetTraceSummaries",
        "xray:BatchGetTraces"
      ],
      "Resource": "*"
    }
  ]
}
```

---

## 4. Dependency Discovery & Evidence Taxonomy

InfraShift extracts relationships between API Gateway, Lambda, and DynamoDB using multi-layered evidence.

### Evidence Classification: OBSERVED vs. INFERRED

- **OBSERVED**: Direct, verified evidence directly obtained from AWS runtime telemetry or configuration.
  - *API Gateway → Lambda*: Explicitly configured API Gateway integration targets (`evidence_type="aws_configuration"`).
  - *Lambda → DynamoDB*: Active execution trace segments recorded by AWS X-Ray (`evidence_type="xray"`).
- **INFERRED**: Indirect evidence inferred from environment variable names or values.
  - *Lambda → DynamoDB*: Environment variable keys matching `TABLE`/`DYNAMO` or pointing to a table name/ARN (`evidence_type="application_metadata"`).
  - **Rule**: Inferred relationships are *never* labeled as observed. If both exist, `OBSERVED` takes precedence.

---

## 5. Running Dependency & Graph Discovery

```python
from aws.discovery import DependencyDiscovery

# Initialize orchestrator
orchestrator = DependencyDiscovery()

# Discover dependencies across API Gateway, Lambda, DynamoDB, and X-Ray
result = orchestrator.discover_dependencies()

print(f"Evidence Status: {result.evidence_status}")
print(f"Total Discovered Dependencies: {len(result.dependencies)}")

for dep in result.dependencies:
    print(f"[{dep.confidence.value.upper()}] {dep.source_resource_id} --({dep.relationship.value})--> {dep.target_resource_id} via {dep.evidence_type.value}")

# Access normalized Dependency Graph
graph = result.graph
print(f"Graph Nodes: {len(graph.nodes)}, Graph Edges: {len(graph.edges)}")
```

---

## 6. Historical Telemetry Connection

Nodes in the dependency graph can be queried for CloudWatch telemetry using the existing `CloudWatchTelemetry` service without logic duplication:

```python
node = result.graph.nodes[0]
telemetry_series = orchestrator.get_resource_telemetry(
    node=node,
    metric_name="Invocations",
    period_seconds=300,
)
```

---

## 7. Handling Missing X-Ray Data & AWS Errors

If X-Ray tracing is disabled, has no trace data for the time window, or fails due to IAM permission denial (`AccessDeniedException`):
- The application **never crashes**.
- Missing trace data is handled gracefully and returns `evidence_status="unavailable"` (or `"inferred"` if config metadata is present) along with an explicit `reason` string.
- No placeholder nodes or fake relationships are generated.

---

## 8. Running Unit Tests

Unit tests mock all AWS API interactions using `unittest.mock` and `botocore`. No cloud connection or AWS credentials are required to run tests.

```bash
python -m pytest aws/tests -v
```

---

## 9. Example Normalized Dependency Graph Output

```json
{
  "nodes": [
    {
      "id": "arn:aws:apigateway:ap-south-1::/restapis/orders-api-id",
      "type": "api_gateway",
      "name": "orders-api",
      "arn": "arn:aws:apigateway:ap-south-1::/restapis/orders-api-id",
      "metadata": {
        "api_id": "orders-api-id",
        "api_name": "orders-api",
        "stages": ["prod"]
      }
    },
    {
      "id": "arn:aws:lambda:ap-south-1:123456789012:function:create-order-fn",
      "type": "lambda",
      "name": "create-order-fn",
      "arn": "arn:aws:lambda:ap-south-1:123456789012:function:create-order-fn",
      "metadata": {
        "function_name": "create-order-fn",
        "runtime": "python3.12"
      }
    },
    {
      "id": "arn:aws:dynamodb:ap-south-1:123456789012:table/OrdersTable",
      "type": "dynamodb",
      "name": "OrdersTable",
      "arn": "arn:aws:dynamodb:ap-south-1:123456789012:table/OrdersTable",
      "metadata": {
        "table_name": "OrdersTable",
        "table_status": "ACTIVE"
      }
    }
  ],
  "edges": [
    {
      "source": "arn:aws:apigateway:ap-south-1::/restapis/orders-api-id",
      "target": "arn:aws:lambda:ap-south-1:123456789012:function:create-order-fn",
      "relationship": "routes_to",
      "evidence": "aws_configuration",
      "confidence": "observed",
      "metadata": {
        "route_path": "/orders",
        "http_method": "POST"
      }
    },
    {
      "source": "arn:aws:lambda:ap-south-1:123456789012:function:create-order-fn",
      "target": "arn:aws:dynamodb:ap-south-1:123456789012:table/OrdersTable",
      "relationship": "accesses",
      "evidence": "xray",
      "confidence": "observed",
      "metadata": {
        "trace_id": "1-5759e988-bd862e3fe1be46a994272793",
        "operation": "PutItem",
        "duration_ms": 30.0
      }
    }
## 10. Code Change → AWS Resource Impact Mapping

InfraShift includes a deterministic impact mapping engine (`ImpactMappingService`) that links code changes to application components, resolves components to discovered AWS resources, traverses the dependency graph, and packages historical CloudWatch telemetry references.

### End-to-End Example Flow

```text
Changed File:
  src/orders/handler.py
        ↓
Mapped Component:
  orders-handler
        ↓
Direct Impact (AWS Lambda):
  arn:aws:lambda:us-east-1:123456789012:function:orders-handler
        ↓
Downstream Dependency (AWS DynamoDB):
  arn:aws:dynamodb:us-east-1:123456789012:table/OrdersTable (via X-Ray trace evidence)
        ↓
Upstream Dependency (AWS API Gateway):
  arn:aws:apigateway:us-east-1::/restapis/api123 (via AWS configuration)
        ↓
Historical Telemetry Attached:
  Lambda: Invocations, Duration, Errors, Throttles
  DynamoDB: ConsumedReadCapacityUnits, ConsumedWriteCapacityUnits, ReadThrottleEvents, WriteThrottleEvents
```

### Running Impact Analysis

```python
from aws.impact import ImpactMappingService, CodeChangeInput, FileChange, FileChangeStatus

# 1. Initialize Impact Mapping Service
service = ImpactMappingService()

# 2. Define input code change (from commit, PR, or CI event)
change_input = CodeChangeInput(
    change_id="PR-102",
    commit_sha="a1b2c3d4e5",
    files_changed=[
        FileChange(path="src/orders/handler.py", status=FileChangeStatus.MODIFIED, additions=25, deletions=5),
        FileChange(path="docs/readme.md", status=FileChangeStatus.MODIFIED, additions=2, deletions=1),
    ]
)

# 3. Analyze impact and generate handoff evidence package
evidence_package = service.analyze_change_impact(change_input)

print(f"Change ID: {evidence_package.change_id}")
print(f"Status: {evidence_package.status}")
print(f"Impacted Resources Count: {len(evidence_package.impacted_resources)}")

for res in evidence_package.impacted_resources:
    print(f"[{res.impact.value.upper()}] {res.resource_type.value}: {res.resource_name} (Confidence: {res.confidence.value})")
```

### Handoff Boundary: `ChangeImpactEvidence` JSON Output

```json
{
  "change_id": "PR-102",
  "status": "partially_mapped",
  "change": {
    "change_id": "PR-102",
    "commit_sha": "a1b2c3d4e5",
    "files_changed": [
      {
        "path": "src/orders/handler.py",
        "status": "modified",
        "additions": 25,
        "deletions": 5
      },
      {
        "path": "docs/readme.md",
        "status": "modified",
        "additions": 2,
        "deletions": 1
      }
    ]
  },
  "changed_files": ["src/orders/handler.py", "docs/readme.md"],
  "mapped_components": [
    {
      "file_path": "src/orders/handler.py",
      "component_name": "orders-handler",
      "resource_id": "arn:aws:lambda:us-east-1:123456789012:function:orders-handler",
      "resource_type": "lambda",
      "evidence_type": "aws_configuration",
      "confidence": "observed",
      "status": "mapped"
    }
  ],
  "impacted_resources": [
    {
      "resource_id": "arn:aws:lambda:us-east-1:123456789012:function:orders-handler",
      "resource_type": "lambda",
      "resource_name": "orders-handler",
      "impact": "direct",
      "confidence": "observed",
      "evidence": [
        {
          "type": "aws_configuration",
          "source": "file_mapping",
          "file": "src/orders/handler.py"
        }
      ],
      "telemetry_metrics": ["Invocations", "Duration", "Errors", "Throttles"]
    },
    {
      "resource_id": "arn:aws:dynamodb:us-east-1:123456789012:table/OrdersTable",
      "resource_type": "dynamodb",
      "resource_name": "OrdersTable",
      "impact": "downstream",
      "confidence": "observed",
      "evidence": [
        {
          "type": "xray",
          "source": "dependency_graph",
          "relationship": "accesses"
        }
      ],
      "telemetry_metrics": ["ConsumedReadCapacityUnits", "ConsumedWriteCapacityUnits", "ReadThrottleEvents", "WriteThrottleEvents"]
    }
  ],
  "impact_paths": [
    {
      "source_resource_id": "arn:aws:lambda:us-east-1:123456789012:function:orders-handler",
      "target_resource_id": "arn:aws:dynamodb:us-east-1:123456789012:table/OrdersTable",
      "path": [
        {
          "resource_id": "arn:aws:lambda:us-east-1:123456789012:function:orders-handler",
          "resource_type": "lambda",
          "relationship": "accesses",
          "impact_type": "direct"
        },
        {
          "resource_id": "arn:aws:dynamodb:us-east-1:123456789012:table/OrdersTable",
          "resource_type": "dynamodb",
          "relationship": "accesses",
          "impact_type": "downstream"
        }
      ],
      "relationship": "accesses",
      "evidence": "xray",
      "confidence": "observed"
    }
  ],
  "telemetry_references": [
    {
      "resource_id": "arn:aws:lambda:us-east-1:123456789012:function:orders-handler",
      "resource_type": "lambda",
      "historical_metrics": ["Invocations", "Duration", "Errors", "Throttles"],
      "namespace": "AWS/Lambda"
    },
    {
      "resource_id": "arn:aws:dynamodb:us-east-1:123456789012:table/OrdersTable",
      "resource_type": "dynamodb",
      "historical_metrics": ["ConsumedReadCapacityUnits", "ConsumedWriteCapacityUnits", "ReadThrottleEvents", "WriteThrottleEvents"],
      "namespace": "AWS/DynamoDB"
    }
  ],
  "unresolved_items": [
    {
      "file_path": "docs/readme.md",
      "status": "unknown",
      "reason": "No application component mapping available."
    }
  ],
## 11. Deployment & Event Tracking Layer

InfraShift tracks deployment events, links them to code changes and impacted AWS resources, enforces lifecycle state validation, deduplicates event streams, and generates `DeploymentSnapshot` records containing `telemetry_anchor_timestamp` for post-deployment CloudWatch verification.

### End-to-End Deployment Lifecycle Flow

```text
Code Change (PR-102 / Commit a1b2c3d4)
        ↓
Impact Analysis (ChangeImpactEvidence: Lambda X, DynamoDB Y)
        ↓
Deployment Event (EventBridge / Pipeline Event: deploy-123)
        ↓
Lifecycle State Transition (Pending → Started → Completed)
        ↓
Deployment Snapshot (snap-deploy-123)
        ↓
Telemetry Anchor Timestamp (completed_at: 2026-09-19T16:01:20Z)
        ↓
AWS Resource IDs (arn:aws:lambda:..., arn:aws:dynamodb:...)
        ↓
Post-Deployment CloudWatch Baseline Metrics
```

### Running Deployment Tracking & EventBridge Ingestion

```python
from aws.events import (
    DeploymentTrackingService,
    EventBridgeIntegration,
    DeploymentEvent,
    DeploymentStatus,
    DeploymentEnvironment,
)

# 1. Initialize Tracking Service & EventBridge Integration
service = DeploymentTrackingService()
eb = EventBridgeIntegration()

# 2. Parse raw EventBridge payload from CodeDeploy / GitHub Actions
raw_payload = {
    "id": "eb-evt-500",
    "detail": {
        "deploymentId": "deploy-123",
        "pull_request_id": "PR-102",
        "git_sha": "a1b2c3d4",
        "env": "STAGING",
        "state": "COMPLETED",
        "startTime": "2026-09-19T16:00:00Z",
        "endTime": "2026-09-19T16:01:20Z",
    }
}

event = eb.parse_eventbridge_payload(raw_payload)

# 3. Record event and associate with ChangeImpactEvidence (if available)
snapshot = service.record_event(event, evidence=evidence_package)

print(f"Snapshot ID: {snapshot.snapshot_id}")
print(f"Deployment Status: {snapshot.status.value}")
print(f"Telemetry Anchor Timestamp: {snapshot.telemetry_anchor_timestamp}")
print(f"Associated Deployed Resources: {len(snapshot.resources)}")
```

### Example `DeploymentSnapshot` JSON Output

```json
{
  "snapshot_id": "snap-deploy-123",
  "deployment_id": "deploy-123",
  "change_id": "PR-102",
  "commit_sha": "a1b2c3d4",
  "environment": "staging",
  "status": "completed",
  "started_at": "2026-09-19T16:00:00Z",
  "completed_at": "2026-09-19T16:01:20Z",
  "resources": [
    {
      "resource_id": "arn:aws:lambda:us-east-1:123456789012:function:orders-handler",
      "resource_type": "lambda",
      "region": "us-east-1",
      "deployment_relationship": "direct"
    },
    {
      "resource_id": "arn:aws:dynamodb:us-east-1:123456789012:table/OrdersTable",
      "resource_type": "dynamodb",
      "region": "us-east-1",
      "deployment_relationship": "downstream"
    }
  ],
  "telemetry_anchor_timestamp": "2026-09-19T16:01:20Z",
## 12. Forecast-vs-Actual AWS Telemetry Loop

InfraShift compares pre-deployment historical baselines with post-deployment actual CloudWatch telemetry windows and evaluates externally supplied forecast predictions from Person 1's forecasting layer.

### Architecture & Data Flow

```text
PRE-DEPLOYMENT
Pre-Deployment Window [completed_at - baseline_minutes, completed_at]
        ↓
Historical CloudWatch Baseline (e.g. Duration = 175.0ms)
        ↓
Externally Ingested Forecast (ResourceForecastInput: predicted = 190.0ms, bounds = [175, 210])
        ↓
DEPLOYMENT (completed_at anchor: 2026-09-19T16:01:20Z)
        ↓
POST-DEPLOYMENT
Post-Deployment Window [completed_at, completed_at + post_minutes]
        ↓
Actual CloudWatch Observation (e.g. Duration = 184.2ms)
        ↓
Deterministic Comparison (absolute_error = 5.8ms, relative_error = 3.05%, within_range = True)
        ↓
Factual Measurement Handoff (DeploymentForecastVsActualResult)
```

### Running Forecast-vs-Actual Comparisons

```python
from aws.telemetry import (
    ForecastVsActualService,
    ResourceForecastInput,
    MetricForecast,
)

# 1. Initialize Comparison Service
comparison_service = ForecastVsActualService()

# 2. Ingest external forecast predictions (from Person 1's forecasting layer)
forecast_input = ResourceForecastInput(
    resource_id="arn:aws:lambda:us-east-1:123456789012:function:orders-handler",
    metric_forecasts={
        "Duration": MetricForecast(predicted_value=190.0, lower_bound=175.0, upper_bound=210.0, unit="Milliseconds"),
        "Invocations": MetricForecast(predicted_value=150.0, lower_bound=130.0, upper_bound=170.0, unit="Count"),
    }
)

# 3. Perform deterministic comparison against deployment snapshot
result = comparison_service.compare_deployment_telemetry(
    snapshot=deployment_snapshot,
    forecasts=[forecast_input],
    baseline_window_minutes=60,
    post_window_minutes=60,
)

print(f"Deployment ID: {result.deployment_id}")
print(f"Comparison Status: {result.status}")

for res_comp in result.resources:
    print(f"Resource: {res_comp.resource_name}")
    for comp in res_comp.comparisons:
        print(f"  [{comp.metric_name}] {comp.message}")
```

### Handoff Output: `DeploymentForecastVsActualResult` JSON

```json
{
  "deployment_id": "deploy-123",
  "change_id": "PR-102",
  "environment": "staging",
  "telemetry_anchor_timestamp": "2026-09-19T16:01:20Z",
  "resources": [
    {
      "resource_id": "arn:aws:lambda:us-east-1:123456789012:function:orders-handler",
      "resource_type": "lambda",
      "resource_name": "orders-handler",
      "comparisons": [
        {
          "metric_name": "Duration",
          "forecast": {
            "predicted_value": 190.0,
            "lower_bound": 175.0,
            "upper_bound": 210.0,
            "unit": "Milliseconds"
          },
          "actual": {
            "metric_name": "Duration",
            "aggregation": "average",
            "value": 184.2,
            "unit": "Milliseconds",
            "datapoint_count": 12,
            "status": "usable"
          },
          "baseline_value": 175.0,
          "absolute_error": 5.8,
          "relative_error": 0.0305,
          "within_forecast_range": true,
          "range_status": "within_range",
          "status": "usable",
          "message": "Metric 'Duration' post-deployment average was 184.2 Milliseconds vs baseline 175.0 Milliseconds (predicted: 190.0, within forecast range [175.0, 210.0]: True)."
        }
      ]
    }
  ],
  "status": "completed",
  "generated_at": "2026-09-19T17:05:00.000000+00:00"
}
```

### Measurement Policy & Non-Causal Guarantee

- **No AI Invention**: Forecast predictions are ingested as-is from external inputs; the AWS layer never generates or alters forecasts.
- **No Data != Zero**: Missing CloudWatch telemetry returns `status="no_data"` with `value=null`.
- **Factual Non-Causal Reporting**: All generated messages state measured observations (e.g. *"actual value was 184.2ms vs baseline 175.0ms"*) without asserting causation.

---

## 13. Final AWS Evidence Integration & Handoff Pipeline

The **AWS Evidence Integration Layer** connects all Person 2 components into a single, traceable, read-only evidence pipeline.

### End-to-End Pipeline Architecture

```text
CODE CHANGE (CodeChangeInput: PR-102)
        ↓
IMPACT MAPPING (ImpactMappingService: Lambda X, DynamoDB Y)
        ↓
DEPLOYMENT EVENT (DeploymentTrackingService: deploy-123)
        ↓
TELEMETRY ANCHOR (telemetry_anchor_timestamp: 2026-09-19T16:01:20Z)
        ↓
PRE-DEPLOYMENT BASELINE (TelemetryLoopService: 60m pre-deployment window)
        ↓
POST-DEPLOYMENT ACTUALS (TelemetryLoopService: 60m post-deployment window)
        ↓
EXTERNAL FORECAST INGESTION (ResourceForecastInput from Person 1)
        ↓
FORECAST-VS-ACTUAL COMPARISON (ForecastVsActualService: absolute & relative error)
        ↓
UNIFIED AWS EVIDENCE PACKAGE (AWSEvidencePackage)
        ↓
HANDOFF TO PERSON 1 (AI / Forecasting) & PERSON 3 (Backend API)
```

### Running the Integration Service

```python
from aws.integration import AWSEvidenceIntegrationService, AWSEvidencePackage
from aws.impact import CodeChangeInput, FileChange
from aws.telemetry import ResourceForecastInput, MetricForecast

# Initialize Integration Service
service = AWSEvidenceIntegrationService()

# 1. Single entrypoint for Person 3 Backend API
package: AWSEvidencePackage = service.analyze_and_assemble(
    change_input=CodeChangeInput(
        change_id="PR-102",
        files_changed=[FileChange(path="src/orders/handler.py")]
    ),
    deployment_id="deploy-123",
    forecasts=[
        ResourceForecastInput(
            resource_id="arn:aws:lambda:us-east-1:123456789012:function:orders-handler",
            metric_forecasts={
                "Duration": MetricForecast(predicted_value=190.0, lower_bound=175.0, upper_bound=210.0, unit="Milliseconds")
            }
        )
    ]
)

print(f"Package Change ID: {package.change_id}")
print(f"Package Status: {package.status}")
print(f"Forecast Status: {package.forecast_status}")
print(f"Read-Only Verified: {package.read_only_verified}")
```

### Handoff Contracts

#### Person 1 (AI / Forecasting Layer) Handoff
Person 1 receives `ChangeImpactEvidence` and `AWSEvidencePackage` containing:
- Discovered AWS resources & dependency paths
- CloudWatch historical baseline metrics
- Telemetry window timestamps (`telemetry_anchor_timestamp`)
- Complete evidence provenance (`observed` vs `inferred`, `aws_configuration` vs `xray`)

Person 1 produces `ResourceForecastInput` and passes it back into the AWS evidence layer for comparison.

#### Person 3 (Backend API Layer) Handoff
Person 3 consumes `AWSEvidenceIntegrationService.analyze_and_assemble(...)` as a clean backend entrypoint, returning a complete `AWSEvidencePackage` object containing change impact, deployment status, pre/post observations, error metrics, and traceability.

### Non-Causal Measurement Policy
> InfraShift does not claim that a measured post-deployment change was caused by the deployment unless causal evidence exists.





