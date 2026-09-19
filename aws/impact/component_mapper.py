"""
Deterministic File-to-Application Component and AWS Resource Mapper.
Associates changed file paths with real discovered AWS resources using deployment metadata,
Lambda handler configurations, and explicit project mapping rules.
Never fabricates mappings or guesses for unmappable files.
"""

import os
import re
import logging
from typing import List, Dict, Optional, Any, Tuple

from aws.models.aws_models import (
    ResourceType,
    NormalizedResource,
    EvidenceType,
    ConfidenceLevel,
)
from aws.impact.code_change_models import ComponentMapping

logger = logging.getLogger("infrashift.aws.impact.component_mapper")


class FileToComponentMapper:
    """
    Deterministic mapper associating file changes with application components and AWS resources.
    """

    def __init__(
        self,
        custom_mappings: Optional[Dict[str, str]] = None,
    ):
        """
        :param custom_mappings: Optional dictionary mapping file paths or directory prefixes
                                to component names or AWS resource names/ARNs.
                                e.g. {"src/orders/service.py": "order-api"}
        """
        self.custom_mappings = custom_mappings or {}

    def map_file_to_resource(
        self,
        file_path: str,
        discovered_resources: List[NormalizedResource],
    ) -> ComponentMapping:
        """
        Map a single file path to an application component and real AWS resource.

        :param file_path: Relative repository file path (e.g. 'src/orders/handler.py').
        :param discovered_resources: List of real AWS resources discovered in the environment.
        :return: ComponentMapping object containing mapping result or 'unknown' status.
        """
        clean_path = file_path.replace("\\", "/")

        # 1. Explicit Custom Mapping Check
        custom_match = self._check_custom_mappings(clean_path, discovered_resources)
        if custom_match:
            return custom_match

        # 2. Lambda Handler Configuration Match
        handler_match = self._check_lambda_handlers(clean_path, discovered_resources)
        if handler_match:
            return handler_match

        # 3. Structured Directory & Naming Pattern Matching
        pattern_match = self._check_path_patterns(clean_path, discovered_resources)
        if pattern_match:
            return pattern_match

        # 4. Fallback for unmappable file (NO GUESSING)
        logger.debug("File '%s' could not be mapped to any discovered AWS resource.", file_path)
        return ComponentMapping(
            file_path=file_path,
            status="unknown",
            reason="No application component mapping available.",
        )

    def _check_custom_mappings(
        self,
        file_path: str,
        discovered_resources: List[NormalizedResource],
    ) -> Optional[ComponentMapping]:
        """Check explicit custom mapping configuration."""
        for pattern, target in self.custom_mappings.items():
            pattern_clean = pattern.replace("\\", "/")
            if file_path == pattern_clean or file_path.startswith(pattern_clean.rstrip("/") + "/"):
                # Search for matching resource
                for res in discovered_resources:
                    if res.resource_name == target or res.resource_id == target:
                        return ComponentMapping(
                            file_path=file_path,
                            component_name=target,
                            resource_id=res.resource_id,
                            resource_type=res.resource_type,
                            evidence_type=EvidenceType.APPLICATION_METADATA,
                            confidence=ConfidenceLevel.OBSERVED,
                            status="mapped",
                        )

                # If custom mapping provided component name but resource not found in AWS
                return ComponentMapping(
                    file_path=file_path,
                    component_name=target,
                    status="unknown",
                    reason=f"Custom mapped component '{target}' not found in discovered AWS resources.",
                )
        return None

    def _check_lambda_handlers(
        self,
        file_path: str,
        discovered_resources: List[NormalizedResource],
    ) -> Optional[ComponentMapping]:
        """Match file path against Lambda handler configurations."""
        base_name, _ = os.path.splitext(file_path)
        file_mod = base_name.replace("/", ".").replace("\\", ".")
        file_stem = os.path.basename(base_name)

        for res in discovered_resources:
            if res.resource_type == ResourceType.LAMBDA:
                meta = res.metadata
                handler = meta.get("handler", "")
                if not handler:
                    continue

                # Extract module portion of handler e.g. "src/orders/handler.lambda_handler" -> "src.orders.handler"
                handler_parts = handler.rsplit(".", 1)
                handler_mod = handler_parts[0].replace("/", ".").replace("\\", ".")

                if file_mod == handler_mod or file_mod.endswith("." + handler_mod) or handler_mod.endswith("." + file_mod) or file_stem == handler_mod:
                    return ComponentMapping(
                        file_path=file_path,
                        component_name=res.resource_name,
                        resource_id=res.resource_id,
                        resource_type=ResourceType.LAMBDA,
                        evidence_type=EvidenceType.AWS_CONFIGURATION,
                        confidence=ConfidenceLevel.OBSERVED,
                        status="mapped",
                    )
        return None


    def _check_path_patterns(
        self,
        file_path: str,
        discovered_resources: List[NormalizedResource],
    ) -> Optional[ComponentMapping]:
        """Extract candidate component name from directory structure and match against AWS resources."""
        parts = [p for p in file_path.split("/") if p]
        if len(parts) < 2:
            return None

        # Look for directory names under common roots: src/, lambdas/, services/, functions/, apps/
        candidate_names: List[str] = []
        for i, part in enumerate(parts[:-1]):
            if part.lower() in ["src", "lambdas", "services", "functions", "apps", "pkg"]:
                if i + 1 < len(parts):
                    candidate_names.append(parts[i + 1])
            else:
                candidate_names.append(part)

        # Also add the file stem itself
        stem = os.path.splitext(parts[-1])[0]
        if stem not in ["index", "main", "handler", "service", "app"]:
            candidate_names.append(stem)

        for candidate in candidate_names:
            c_clean = candidate.lower().replace("_", "-")
            for res in discovered_resources:
                r_name_clean = res.resource_name.lower().replace("_", "-")
                if c_clean == r_name_clean or c_clean in r_name_clean or r_name_clean in c_clean:
                    return ComponentMapping(
                        file_path=file_path,
                        component_name=res.resource_name,
                        resource_id=res.resource_id,
                        resource_type=res.resource_type,
                        evidence_type=EvidenceType.APPLICATION_METADATA,
                        confidence=ConfidenceLevel.INFERRED,
                        status="mapped",
                    )
        return None
