"""
AWS X-Ray Tracing metadata module.
Provides interface for inspecting X-Ray service graphs, trace summaries, and trace segment evidence.
Normalizes X-Ray trace evidence for AWS Lambda, DynamoDB, and API Gateway dependencies.
"""

import json
import logging
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional, Tuple, Union
from botocore.exceptions import BotoCoreError, ClientError

from aws.config.aws_config import AWSClientFactory, AWSConfig
from aws.models.aws_models import (
    ResourceType,
    NormalizedDependency,
    EvidenceType,
    ConfidenceLevel,
    RelationshipType,
    XRayTraceEvidence,
)

logger = logging.getLogger("infrashift.aws.tracing.xray")


class XRayTracing:
    """Retrieves X-Ray service graph and trace summary data."""

    def __init__(self, client_factory: Optional[AWSClientFactory] = None, config: Optional[AWSConfig] = None):
        if client_factory:
            self.factory = client_factory
        else:
            self.factory = AWSClientFactory(config=config or AWSConfig())

    def get_client(self):
        return self.factory.get_client("xray")

    def _parse_datetime(self, dt_val: Union[datetime, str]) -> datetime:
        """Helper to ensure datetime object."""
        if isinstance(dt_val, datetime):
            return dt_val
        clean_str = str(dt_val).rstrip("Z")
        return datetime.fromisoformat(clean_str)

    def get_service_graph(self, start_time: Any, end_time: Any) -> List[Dict[str, Any]]:
        """
        Fetch X-Ray service graph showing dependencies between Lambda, DynamoDB, API Gateway.
        """
        try:
            start_dt = self._parse_datetime(start_time)
            end_dt = self._parse_datetime(end_time)
            client = self.get_client()
            response = client.get_service_graph(
                StartTime=start_dt,
                EndTime=end_dt,
            )
            return response.get("Services", [])
        except (BotoCoreError, ClientError) as e:
            logger.error("Failed to retrieve X-Ray service graph: %s", str(e))
            return []
        except Exception as e:
            logger.error("Unexpected error retrieving X-Ray service graph: %s", str(e))
            return []

    def get_trace_summaries(
        self,
        start_time: Any,
        end_time: Any,
        filter_expression: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Fetch X-Ray trace summaries for a target time window.
        """
        try:
            start_dt = self._parse_datetime(start_time)
            end_dt = self._parse_datetime(end_time)
            client = self.get_client()

            kwargs: Dict[str, Any] = {
                "StartTime": start_dt,
                "EndTime": end_dt,
            }
            if filter_expression:
                kwargs["FilterExpression"] = filter_expression

            response = client.get_trace_summaries(**kwargs)
            return response.get("TraceSummaries", [])
        except (BotoCoreError, ClientError) as e:
            logger.error("Failed to retrieve X-Ray trace summaries: %s", str(e))
            return []
        except Exception as e:
            logger.error("Unexpected error retrieving trace summaries: %s", str(e))
            return []

    def batch_get_traces(self, trace_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Fetch full X-Ray trace documents for a list of trace IDs.
        """
        if not trace_ids:
            return []
        try:
            client = self.get_client()
            response = client.batch_get_traces(TraceIds=trace_ids)
            return response.get("Traces", [])
        except (BotoCoreError, ClientError) as e:
            logger.error("Failed to fetch batch X-Ray traces: %s", str(e))
            return []
        except Exception as e:
            logger.error("Unexpected error fetching batch traces: %s", str(e))
            return []

    def discover_trace_evidence(
        self,
        start_time: Optional[Any] = None,
        end_time: Optional[Any] = None,
        filter_expression: Optional[str] = None,
    ) -> Tuple[List[XRayTraceEvidence], List[NormalizedDependency]]:
        """
        Extract observed X-Ray trace evidence and dependencies between services.
        Combines service graph evaluation and trace document segment parsing.
        """
        now = datetime.now(timezone.utc)
        end_dt = self._parse_datetime(end_time) if end_time else now
        start_dt = self._parse_datetime(start_time) if start_time else (end_dt - timedelta(hours=1))

        evidences: List[XRayTraceEvidence] = []
        dependencies: List[NormalizedDependency] = []

        # 1. Parse Service Graph
        services = self.get_service_graph(start_dt, end_dt)
        service_map: Dict[int, Dict[str, Any]] = {}
        for svc in services:
            ref_id = svc.get("ReferenceId")
            if ref_id is not None:
                service_map[ref_id] = svc

        region = self.factory.config.region_name

        for svc in services:
            svc_name = svc.get("Name", "")
            svc_type = svc.get("Type", "")
            svc_arn = svc.get("AccountId")  # Fallback if available

            for edge in svc.get("Edges", []):
                target_id = edge.get("TargetId")
                target_svc = service_map.get(target_id, {})
                target_name = target_svc.get("Name", "")
                target_type = target_svc.get("Type", "")

                source_res_type, source_arn = self._map_xray_service_to_resource(svc_type, svc_name, region)
                target_res_type, target_arn = self._map_xray_service_to_resource(target_type, target_name, region)

                if source_res_type and target_res_type:
                    rel_type = RelationshipType.INVOKES if source_res_type == ResourceType.API_GATEWAY else RelationshipType.ACCESSES
                    dep = NormalizedDependency(
                        source_resource_id=source_arn,
                        source_type=source_res_type,
                        target_resource_id=target_arn,
                        target_type=target_res_type,
                        relationship=rel_type,
                        evidence_type=EvidenceType.XRAY,
                        confidence=ConfidenceLevel.OBSERVED,
                        observed_at=start_dt.isoformat(),
                        metadata={
                            "source_service_name": svc_name,
                            "target_service_name": target_name,
                            "evidence_source": "xray_service_graph",
                        },
                    )
                    dependencies.append(dep)

        # 2. Parse Detailed Trace Documents if summaries available
        summaries = self.get_trace_summaries(start_dt, end_dt, filter_expression)
        trace_ids = [s["Id"] for s in summaries if "Id" in s][:10]  # Cap batch to 10 for performance

        if trace_ids:
            traces = self.batch_get_traces(trace_ids)
            for trace in traces:
                t_id = trace.get("Id", "")
                segments = trace.get("Segments", [])
                for seg_wrapper in segments:
                    doc_raw = seg_wrapper.get("Document")
                    if not doc_raw:
                        continue
                    try:
                        doc = json.loads(doc_raw) if isinstance(doc_raw, str) else doc_raw
                        extracted_evs, extracted_deps = self._parse_segment_document(doc, t_id, region)
                        evidences.extend(extracted_evs)
                        dependencies.extend(extracted_deps)
                    except Exception as e:
                        logger.warning("Error parsing X-Ray trace segment document for trace '%s': %s", t_id, e)

        return evidences, dependencies

    def _map_xray_service_to_resource(
        self,
        svc_type: str,
        svc_name: str,
        region: str,
    ) -> Tuple[Optional[ResourceType], Optional[str]]:
        """Map X-Ray service node type and name to normalized ResourceType and ARN."""
        t_lower = svc_type.lower()
        if "lambda" in t_lower:
            arn = svc_name if svc_name.startswith("arn:aws:lambda:") else f"arn:aws:lambda:{region}::function:{svc_name}"
            return ResourceType.LAMBDA, arn
        elif "dynamodb" in t_lower:
            arn = svc_name if svc_name.startswith("arn:aws:dynamodb:") else f"arn:aws:dynamodb:{region}::table/{svc_name}"
            return ResourceType.DYNAMODB, arn
        elif "apigateway" in t_lower or "api" in t_lower:
            arn = svc_name if svc_name.startswith("arn:aws:apigateway:") else f"arn:aws:apigateway:{region}::/apis/{svc_name}"
            return ResourceType.API_GATEWAY, arn
        return None, None

    def _parse_segment_document(
        self,
        doc: Dict[str, Any],
        trace_id: str,
        region: str,
    ) -> Tuple[List[XRayTraceEvidence], List[NormalizedDependency]]:
        """Parse X-Ray trace document segment and subsegments for direct resource calls."""
        evidences: List[XRayTraceEvidence] = []
        dependencies: List[NormalizedDependency] = []

        seg_name = doc.get("name", "")
        origin = doc.get("origin", "")
        start_time = doc.get("start_time", 0.0)
        end_time = doc.get("end_time", start_time)
        duration_ms = round((end_time - start_time) * 1000.0, 2) if end_time >= start_time else None

        # Check subsegments for downstream AWS service calls (e.g., DynamoDB)
        subsegments = doc.get("subsegments", [])
        for sub in subsegments:
            sub_name = sub.get("name", "")
            namespace = sub.get("namespace", "")
            aws_info = sub.get("aws", {})

            # Identify DynamoDB subsegments
            table_name = aws_info.get("table_name") or aws_info.get("resource_names", [None])[0] or sub_name
            is_dynamo = namespace == "aws" or "dynamo" in sub_name.lower() or "table" in str(table_name).lower()

            if is_dynamo and table_name:
                source_arn = seg_name if seg_name.startswith("arn:aws:lambda:") else f"arn:aws:lambda:{region}::function:{seg_name}"
                target_arn = table_name if str(table_name).startswith("arn:aws:dynamodb:") else f"arn:aws:dynamodb:{region}::table/{table_name}"

                sub_start = sub.get("start_time", start_time)
                sub_end = sub.get("end_time", sub_start)
                sub_dur_ms = round((sub_end - sub_start) * 1000.0, 2) if sub_end >= sub_start else duration_ms

                evidence = XRayTraceEvidence(
                    trace_id=trace_id,
                    timestamp=datetime.fromtimestamp(start_time, tz=timezone.utc).isoformat() if start_time else datetime.now(timezone.utc).isoformat(),
                    source={"type": ResourceType.LAMBDA.value, "resource_id": source_arn},
                    target={"type": ResourceType.DYNAMODB.value, "resource_id": target_arn},
                    duration_ms=sub_dur_ms,
                    error=sub.get("error", False) or doc.get("error", False),
                    fault=sub.get("fault", False) or doc.get("fault", False),
                    evidence_type=EvidenceType.XRAY,
                    confidence=ConfidenceLevel.OBSERVED,
                )
                evidences.append(evidence)


                dep = NormalizedDependency(
                    source_resource_id=source_arn,
                    source_type=ResourceType.LAMBDA,
                    target_resource_id=target_arn,
                    target_type=ResourceType.DYNAMODB,
                    relationship=RelationshipType.ACCESSES,
                    evidence_type=EvidenceType.XRAY,
                    confidence=ConfidenceLevel.OBSERVED,
                    observed_at=evidence.timestamp,
                    metadata={
                        "trace_id": trace_id,
                        "operation": aws_info.get("operation"),
                        "duration_ms": sub_dur_ms,
                        "error": evidence.error,
                        "fault": evidence.fault,
                    },
                )
                dependencies.append(dep)

        return evidences, dependencies

