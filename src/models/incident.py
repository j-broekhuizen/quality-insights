"""Pydantic models for incident tracking data."""

from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class Severity(str, Enum):
    """Incident severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Incident(BaseModel):
    """Represents a single incident."""
    id: str = Field(..., description="Incident identifier (e.g., INC-301)")
    title: str = Field(..., description="Incident title/description")
    severity: Severity = Field(..., description="Incident severity level")
    reported_at: datetime = Field(..., description="Incident report timestamp")
    resolved_at: datetime | None = Field(None, description="Incident resolution timestamp")
    affected_users: int = Field(..., ge=0, description="Number of users affected")
    root_cause: str | None = Field(None, description="Root cause analysis")

    @property
    def is_resolved(self) -> bool:
        """Check if incident is resolved."""
        return self.resolved_at is not None

    @property
    def time_to_resolve_hours(self) -> float | None:
        """Calculate time to resolve in hours."""
        if not self.is_resolved or self.resolved_at is None:
            return None
        delta = self.resolved_at - self.reported_at
        return round(delta.total_seconds() / 3600, 2)


class IncidentMetrics(BaseModel):
    """Aggregated incident metrics."""
    incidents: list[Incident] = Field(default_factory=list, description="List of incidents")

    @property
    def total_incidents(self) -> int:
        """Total number of incidents."""
        return len(self.incidents)

    @property
    def critical_count(self) -> int:
        """Number of critical incidents."""
        return sum(1 for inc in self.incidents if inc.severity == Severity.CRITICAL)

    @property
    def high_count(self) -> int:
        """Number of high severity incidents."""
        return sum(1 for inc in self.incidents if inc.severity == Severity.HIGH)

    @property
    def medium_count(self) -> int:
        """Number of medium severity incidents."""
        return sum(1 for inc in self.incidents if inc.severity == Severity.MEDIUM)

    @property
    def low_count(self) -> int:
        """Number of low severity incidents."""
        return sum(1 for inc in self.incidents if inc.severity == Severity.LOW)

    @property
    def resolved_count(self) -> int:
        """Number of resolved incidents."""
        return sum(1 for inc in self.incidents if inc.is_resolved)

    @property
    def mean_time_to_resolve(self) -> float:
        """Calculate mean time to resolve (MTTR) in hours."""
        resolved_times = [
            inc.time_to_resolve_hours
            for inc in self.incidents
            if inc.time_to_resolve_hours is not None
        ]
        if not resolved_times:
            return 0.0
        return round(sum(resolved_times) / len(resolved_times), 2)
