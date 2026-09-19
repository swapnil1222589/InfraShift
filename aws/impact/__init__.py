"""
AWS Code Change to Resource Impact Mapping Module.
Provides deterministic file-to-component mapping, graph traversal, and ChangeImpactEvidence package generation.
"""

from .code_change_models import (
    ImpactType,
    FileChangeStatus,
    FileChange,
    CodeChangeInput,
    ComponentMapping,
    ImpactedResource,
    ImpactPathStep,
    ImpactPath,
    ResourceTelemetryReference,
    UnresolvedMapping,
    ChangeImpactEvidence,
)
from .component_mapper import FileToComponentMapper
from .impact_mapping import ImpactMappingService

__all__ = [
    "ImpactType",
    "FileChangeStatus",
    "FileChange",
    "CodeChangeInput",
    "ComponentMapping",
    "ImpactedResource",
    "ImpactPathStep",
    "ImpactPath",
    "ResourceTelemetryReference",
    "UnresolvedMapping",
    "ChangeImpactEvidence",
    "FileToComponentMapper",
    "ImpactMappingService",
]
