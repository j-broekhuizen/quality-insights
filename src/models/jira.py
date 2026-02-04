"""Pydantic models for Jira data structures."""

from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class TicketStatus(str, Enum):
    """Jira ticket status."""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    BLOCKED = "blocked"


class JiraTicket(BaseModel):
    """Represents a single Jira ticket."""
    id: str = Field(..., description="Ticket ID (e.g., QUAL-101)")
    title: str = Field(..., description="Ticket title/summary")
    status: TicketStatus = Field(..., description="Current ticket status")
    story_points: int = Field(..., ge=0, description="Story point estimate")
    assigned_to: str = Field(..., description="Assignee name")
    created_at: datetime = Field(..., description="Ticket creation timestamp")
    completed_at: datetime | None = Field(None, description="Ticket completion timestamp")

    @property
    def is_completed(self) -> bool:
        """Check if ticket is completed."""
        return self.status == TicketStatus.DONE and self.completed_at is not None


class SprintMetrics(BaseModel):
    """Aggregated metrics for a sprint."""
    sprint_name: str = Field(..., description="Sprint identifier")
    start_date: str = Field(..., description="Sprint start date (YYYY-MM-DD)")
    end_date: str = Field(..., description="Sprint end date (YYYY-MM-DD)")
    planned_points: int = Field(..., ge=0, description="Total planned story points")
    completed_points: int = Field(..., ge=0, description="Completed story points")
    tickets: list[JiraTicket] = Field(default_factory=list, description="Sprint tickets")

    @property
    def velocity(self) -> float:
        """Calculate sprint velocity (completed/planned)."""
        if self.planned_points == 0:
            return 0.0
        return round(self.completed_points / self.planned_points * 100, 2)

    @property
    def completion_rate(self) -> str:
        """Human-readable completion rate."""
        return f"{self.velocity}%"
