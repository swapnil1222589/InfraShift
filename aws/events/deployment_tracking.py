"""
Deployment Tracking Service and Repository.
Manages deployment event ingestion, code change & resource associations,
lifecycle transition validation, event deduplication, and deployment snapshot persistence.
"""

import threading
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Set, Tuple, Any

from aws.events.event_models import (
    DeploymentEvent,
    DeploymentStatus,
    DeploymentEnvironment,
    DeployedResource,
    DeploymentSnapshot,
)
from aws.impact.code_change_models import ChangeImpactEvidence

logger = logging.getLogger("infrashift.aws.events.tracking")


# Valid lifecycle state transitions
VALID_TRANSITIONS: Dict[DeploymentStatus, Set[DeploymentStatus]] = {
    DeploymentStatus.PENDING: {DeploymentStatus.PENDING, DeploymentStatus.STARTED, DeploymentStatus.FAILED, DeploymentStatus.CANCELLED},
    DeploymentStatus.STARTED: {DeploymentStatus.STARTED, DeploymentStatus.COMPLETED, DeploymentStatus.FAILED, DeploymentStatus.CANCELLED},
    DeploymentStatus.COMPLETED: {DeploymentStatus.COMPLETED},
    DeploymentStatus.FAILED: {DeploymentStatus.FAILED},
    DeploymentStatus.CANCELLED: {DeploymentStatus.CANCELLED},
    DeploymentStatus.UNKNOWN: {DeploymentStatus.PENDING, DeploymentStatus.STARTED, DeploymentStatus.COMPLETED, DeploymentStatus.FAILED, DeploymentStatus.CANCELLED, DeploymentStatus.UNKNOWN},
}


class DeploymentRepository:
    """
    Thread-safe repository for persisting and querying deployment snapshots.
    Provides lookup indexes by deployment_id, change_id, commit_sha, and environment.
    """

    def __init__(self):
        self._lock = threading.RLock()
        self._snapshots: Dict[str, DeploymentSnapshot] = {}
        self._change_index: Dict[str, List[str]] = {}
        self._commit_index: Dict[str, List[str]] = {}
        self._seen_events: Set[str] = set()

    def save_snapshot(self, snapshot: DeploymentSnapshot) -> None:
        """Save or update a deployment snapshot and update indexes."""
        with self._lock:
            self._snapshots[snapshot.deployment_id] = snapshot

            if snapshot.change_id:
                if snapshot.change_id not in self._change_index:
                    self._change_index[snapshot.change_id] = []
                if snapshot.deployment_id not in self._change_index[snapshot.change_id]:
                    self._change_index[snapshot.change_id].append(snapshot.deployment_id)

            if snapshot.commit_sha:
                if snapshot.commit_sha not in self._commit_index:
                    self._commit_index[snapshot.commit_sha] = []
                if snapshot.deployment_id not in self._commit_index[snapshot.commit_sha]:
                    self._commit_index[snapshot.commit_sha].append(snapshot.deployment_id)

    def get_by_id(self, deployment_id: str) -> Optional[DeploymentSnapshot]:
        """Fetch deployment snapshot by deployment_id."""
        with self._lock:
            return self._snapshots.get(deployment_id)

    def find_by_change(self, change_id: str) -> List[DeploymentSnapshot]:
        """Fetch all deployment snapshots for a specific change_id."""
        with self._lock:
            dep_ids = self._change_index.get(change_id, [])
            return [self._snapshots[did] for did in dep_ids if did in self._snapshots]

    def find_by_commit(self, commit_sha: str) -> List[DeploymentSnapshot]:
        """Fetch all deployment snapshots for a specific commit_sha."""
        with self._lock:
            dep_ids = self._commit_index.get(commit_sha, [])
            return [self._snapshots[did] for did in dep_ids if did in self._snapshots]

    def is_event_processed(self, dedup_key: str) -> bool:
        """Check if event deduplication key has already been processed."""
        with self._lock:
            return dedup_key in self._seen_events

    def mark_event_processed(self, dedup_key: str) -> None:
        """Mark event deduplication key as processed."""
        with self._lock:
            self._seen_events.add(dedup_key)

    def list_snapshots(
        self,
        environment: Optional[DeploymentEnvironment] = None,
        status: Optional[DeploymentStatus] = None,
    ) -> List[DeploymentSnapshot]:
        """List all snapshots with optional environment and status filtering."""
        with self._lock:
            results = list(self._snapshots.values())
            if environment:
                results = [s for s in results if s.environment == environment]
            if status:
                results = [s for s in results if s.status == status]
            return results


class DeploymentTrackingService:
    """
    Orchestrator for recording deployment events, validating lifecycles, and creating snapshots.
    """

    def __init__(self, repository: Optional[DeploymentRepository] = None):
        self.repository = repository or DeploymentRepository()

    def record_event(
        self,
        event: DeploymentEvent,
        evidence: Optional[ChangeImpactEvidence] = None,
    ) -> DeploymentSnapshot:
        """
        Record a deployment event, validate lifecycle, associate resources & code change, and save snapshot.

        :param event: Normalized DeploymentEvent.
        :param evidence: Optional ChangeImpactEvidence package containing impacted AWS resources.
        :return: Updated DeploymentSnapshot.
        """
        dedup_key = f"{event.event_id}:{event.deployment_id}:{event.status.value}"
        if self.repository.is_event_processed(dedup_key):
            logger.info("Event '%s' for deployment '%s' already processed. Returning existing snapshot.", event.event_id, event.deployment_id)
            existing = self.repository.get_by_id(event.deployment_id)
            if existing:
                return existing

        # Fetch existing snapshot for lifecycle validation
        existing_snapshot = self.repository.get_by_id(event.deployment_id)

        # Validate Lifecycle Transition
        if existing_snapshot:
            current_status = existing_snapshot.status
            target_status = event.status
            allowed = VALID_TRANSITIONS.get(current_status, {current_status})
            if target_status not in allowed:
                logger.warning(
                    "Invalid lifecycle transition for deployment '%s': %s -> %s. Rejecting transition.",
                    event.deployment_id,
                    current_status.value,
                    target_status.value,
                )
                return existing_snapshot

        # Associate Code Change identifiers if provided in evidence
        change_id = event.change_id
        commit_sha = event.commit_sha
        if evidence:
            change_id = change_id or evidence.change_id
            commit_sha = commit_sha or evidence.change.commit_sha

        # Associate Deployed Resources
        merged_resources_map: Dict[str, DeployedResource] = {}

        # 1. Existing resources if any
        if existing_snapshot:
            for r in existing_snapshot.resources:
                merged_resources_map[r.resource_id] = r

        # 2. Resources from event
        for r in event.resources:
            merged_resources_map[r.resource_id] = r

        # 3. Resources from ChangeImpactEvidence
        if evidence:
            for ir in evidence.impacted_resources:
                if ir.resource_id not in merged_resources_map:
                    merged_resources_map[ir.resource_id] = DeployedResource(
                        resource_id=ir.resource_id,
                        resource_type=ir.resource_type,
                        region=event.region,
                        deployment_relationship=ir.impact.value,
                    )

        # Preserve timestamps (null if unavailable)
        started_at = event.started_at or (existing_snapshot.started_at if existing_snapshot else None)
        completed_at = event.completed_at or (existing_snapshot.completed_at if existing_snapshot else None)

        # Determine Telemetry Anchor Timestamp
        telemetry_anchor = completed_at if event.status == DeploymentStatus.COMPLETED else None

        snapshot = DeploymentSnapshot(
            snapshot_id=f"snap-{event.deployment_id}",
            deployment_id=event.deployment_id,
            change_id=change_id,
            commit_sha=commit_sha,
            environment=event.environment,
            status=event.status,
            started_at=started_at,
            completed_at=completed_at,
            resources=list(merged_resources_map.values()),
            telemetry_anchor_timestamp=telemetry_anchor,
        )

        self.repository.save_snapshot(snapshot)
        self.repository.mark_event_processed(dedup_key)

        logger.info("Recorded deployment snapshot '%s' (Status: %s, Resources: %d)", snapshot.snapshot_id, snapshot.status.value, len(snapshot.resources))
        return snapshot

    def get_deployment(self, deployment_id: str) -> Optional[DeploymentSnapshot]:
        """Lookup deployment snapshot by deployment_id."""
        return self.repository.get_by_id(deployment_id)

    def find_by_change(self, change_id: str) -> List[DeploymentSnapshot]:
        """Find deployment snapshots by change_id."""
        return self.repository.find_by_change(change_id)

    def find_by_commit(self, commit_sha: str) -> List[DeploymentSnapshot]:
        """Find deployment snapshots by commit_sha."""
        return self.repository.find_by_commit(commit_sha)

    def list_deployments(
        self,
        environment: Optional[DeploymentEnvironment] = None,
        status: Optional[DeploymentStatus] = None,
    ) -> List[DeploymentSnapshot]:
        """List deployment snapshots with optional filters."""
        return self.repository.list_snapshots(environment=environment, status=status)
