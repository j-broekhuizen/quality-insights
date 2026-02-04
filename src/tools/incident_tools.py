"""Incident tracking and analysis tools."""

from datetime import datetime, timedelta, timezone
from collections import defaultdict
from langchain_core.tools import tool
from ..data.mock_data import load_incident_data


@tool
def get_incident_summary(severity: str | None = None, days: int = 30) -> dict:
    """Get incident summary for specified time period.

    Args:
        severity: Optional severity filter (critical, high, medium, low).
                 If None, includes all severity levels.
        days: Number of days to look back (default: 30).

    Returns:
        Dictionary with incident metrics including:
        - total_incidents: Total number of incidents in period
        - by_severity: Breakdown of incidents by severity level
        - resolved: Number of resolved incidents
        - unresolved: Number of unresolved incidents
        - affected_users_total: Total users affected across all incidents
        - time_period: Description of analysis period
        - incidents: List of incident details
    """
    data = load_incident_data()
    incidents = data["incidents"]

    # Filter by date range
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
    recent_incidents = [
        inc
        for inc in incidents
        if datetime.fromisoformat(inc["reported_at"].replace("Z", "+00:00"))
        >= cutoff_date
    ]

    # Filter by severity if specified
    if severity:
        severity_lower = severity.lower()
        recent_incidents = [
            inc for inc in recent_incidents if inc["severity"] == severity_lower
        ]

    # Calculate metrics
    total = len(recent_incidents)
    resolved = sum(1 for inc in recent_incidents if inc["resolved_at"] is not None)
    unresolved = total - resolved

    # Severity breakdown
    by_severity = defaultdict(int)
    for inc in recent_incidents:
        by_severity[inc["severity"]] += 1

    # Total affected users
    affected_users = sum(inc["affected_users"] for inc in recent_incidents)

    return {
        "total_incidents": total,
        "by_severity": dict(by_severity),
        "resolved": resolved,
        "unresolved": unresolved,
        "affected_users_total": affected_users,
        "time_period": f"Last {days} days",
        "severity_filter": severity if severity else "all",
        "incidents": [
            {
                "id": inc["id"],
                "title": inc["title"],
                "severity": inc["severity"],
                "reported_at": inc["reported_at"],
                "resolved": inc["resolved_at"] is not None,
                "affected_users": inc["affected_users"],
            }
            for inc in recent_incidents
        ],
    }


@tool
def get_mttr_by_severity() -> dict:
    """Calculate mean time to resolve (MTTR) by incident severity.

    MTTR is calculated only for resolved incidents and measured in hours.

    Returns:
        Dictionary mapping severity levels to MTTR including:
        - mttr_by_severity: Dictionary of severity levels and their MTTR in hours
        - overall_mttr: Average MTTR across all severities
        - analysis_note: Description of calculation methodology
    """
    data = load_incident_data()
    incidents = data["incidents"]

    # Calculate MTTR by severity
    mttr_by_severity = {}
    severity_times = defaultdict(list)

    for inc in incidents:
        if inc["resolved_at"] is not None:
            reported = datetime.fromisoformat(inc["reported_at"].replace("Z", "+00:00"))
            resolved = datetime.fromisoformat(inc["resolved_at"].replace("Z", "+00:00"))
            time_to_resolve = (resolved - reported).total_seconds() / 3600  # hours
            severity_times[inc["severity"]].append(time_to_resolve)

    # Calculate mean for each severity
    for severity, times in severity_times.items():
        mttr = sum(times) / len(times) if times else 0.0
        mttr_by_severity[severity] = round(mttr, 2)

    # Calculate overall MTTR
    all_times = [time for times in severity_times.values() for time in times]
    overall_mttr = round(sum(all_times) / len(all_times), 2) if all_times else 0.0

    # Count resolved incidents by severity
    resolved_counts = {
        severity: len(times) for severity, times in severity_times.items()
    }

    return {
        "mttr_by_severity": mttr_by_severity,
        "overall_mttr": overall_mttr,
        "resolved_incidents_by_severity": resolved_counts,
        "total_resolved_incidents": len(all_times),
        "analysis_note": "MTTR calculated in hours for resolved incidents only",
    }
