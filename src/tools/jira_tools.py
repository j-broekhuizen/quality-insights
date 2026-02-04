"""Jira analysis tools for sprint metrics and velocity tracking."""

from langchain_core.tools import tool
from ..data.mock_data import load_jira_data


@tool
def get_sprint_metrics(sprint_name: str | None = None) -> dict:
    """Get sprint metrics including velocity and completion rate.

    Args:
        sprint_name: Optional sprint name to filter (e.g., 'Sprint 2024-12-2').
                    If None, returns metrics for the most recent sprint.

    Returns:
        Dictionary with sprint metrics including:
        - sprint_name: Name of the sprint
        - planned_points: Total planned story points
        - completed_points: Total completed story points
        - velocity: Completion percentage
        - total_tickets: Total number of tickets
        - completed_tickets: Number of completed tickets
        - in_progress_tickets: Number of in-progress tickets
        - blocked_tickets: Number of blocked tickets
        - date_range: Sprint start and end dates
    """
    data = load_jira_data()
    sprints = data["sprints"]

    # Get specific sprint or latest
    if sprint_name:
        sprint = next((s for s in sprints if s["sprint_name"] == sprint_name), None)
        if not sprint:
            return {"error": f"Sprint '{sprint_name}' not found"}
    else:
        sprint = sprints[-1]  # Latest sprint

    # Calculate metrics
    tickets = sprint["tickets"]
    completed = [t for t in tickets if t["status"] == "done"]
    in_progress = [t for t in tickets if t["status"] == "in_progress"]
    blocked = [t for t in tickets if t["status"] == "blocked"]

    velocity = (
        (sprint["completed_points"] / sprint["planned_points"] * 100)
        if sprint["planned_points"] > 0
        else 0.0
    )

    return {
        "sprint_name": sprint["sprint_name"],
        "planned_points": sprint["planned_points"],
        "completed_points": sprint["completed_points"],
        "velocity": round(velocity, 2),
        "total_tickets": len(tickets),
        "completed_tickets": len(completed),
        "in_progress_tickets": len(in_progress),
        "blocked_tickets": len(blocked),
        "date_range": f"{sprint['start_date']} to {sprint['end_date']}",
    }


@tool
def get_velocity_trend(num_sprints: int = 6) -> dict:
    """Analyze velocity trends over recent sprints.

    Args:
        num_sprints: Number of recent sprints to analyze (default: 6).

    Returns:
        Dictionary with velocity trend analysis including:
        - sprints: List of sprint names and their velocities
        - average_velocity: Mean velocity across all sprints
        - velocity_change: Percentage change from first to last sprint
        - trend: Description of trend (improving, declining, stable)
        - lowest_velocity_sprint: Sprint with lowest velocity
        - highest_velocity_sprint: Sprint with highest velocity
    """
    data = load_jira_data()
    sprints = data["sprints"][-num_sprints:]  # Get most recent N sprints

    # Calculate velocities
    sprint_velocities = []
    for sprint in sprints:
        velocity = (
            (sprint["completed_points"] / sprint["planned_points"] * 100)
            if sprint["planned_points"] > 0
            else 0.0
        )
        sprint_velocities.append(
            {"sprint_name": sprint["sprint_name"], "velocity": round(velocity, 2)}
        )

    # Calculate statistics
    velocities = [sv["velocity"] for sv in sprint_velocities]
    avg_velocity = sum(velocities) / len(velocities) if velocities else 0.0

    # Determine trend
    if len(velocities) >= 2:
        first_velocity = velocities[0]
        last_velocity = velocities[-1]
        velocity_change = (
            ((last_velocity - first_velocity) / first_velocity * 100)
            if first_velocity > 0
            else 0.0
        )

        if velocity_change > 5:
            trend = "improving"
        elif velocity_change < -5:
            trend = "declining"
        else:
            trend = "stable"
    else:
        velocity_change = 0.0
        trend = "insufficient_data"

    # Find lowest and highest
    min_sprint = min(sprint_velocities, key=lambda x: x["velocity"])
    max_sprint = max(sprint_velocities, key=lambda x: x["velocity"])

    return {
        "sprints": sprint_velocities,
        "average_velocity": round(avg_velocity, 2),
        "velocity_change": round(velocity_change, 2),
        "trend": trend,
        "lowest_velocity_sprint": min_sprint,
        "highest_velocity_sprint": max_sprint,
        "analysis_period": f"Last {num_sprints} sprints",
    }
