"""Pydantic models for quality report output."""

from pydantic import BaseModel, Field
from datetime import datetime
from .incident import Severity


class ProblemArea(BaseModel):
    """Represents a problem area identified in quality analysis."""
    category: str = Field(..., description="Problem category (velocity, quality, incidents)")
    description: str = Field(..., description="Detailed problem description")
    severity: Severity = Field(..., description="Problem severity level")
    recommendations: list[str] = Field(default_factory=list, description="Recommended actions")

    @property
    def is_critical(self) -> bool:
        """Check if problem is critical."""
        return self.severity == Severity.CRITICAL


class QualityReport(BaseModel):
    """Complete quality report with analysis and recommendations."""
    generated_at: datetime = Field(default_factory=datetime.now, description="Report generation timestamp")
    team_name: str = Field(..., description="Team being analyzed")
    jira_summary: str = Field(..., description="Jira analysis summary")
    zephyr_summary: str = Field(..., description="Zephyr test quality summary")
    incident_summary: str = Field(..., description="Incident analysis summary")
    problem_areas: list[ProblemArea] = Field(default_factory=list, description="Identified problem areas")
    executive_summary: str = Field(..., description="Executive-level summary with key insights")

    @property
    def critical_problems(self) -> list[ProblemArea]:
        """Get critical problem areas."""
        return [p for p in self.problem_areas if p.is_critical]

    @property
    def has_critical_issues(self) -> bool:
        """Check if report contains critical issues."""
        return len(self.critical_problems) > 0

    def to_markdown(self) -> str:
        """Convert report to markdown format."""
        lines = [
            f"# Quality Report: {self.team_name}",
            f"*Generated: {self.generated_at.strftime('%Y-%m-%d %H:%M:%S')}*",
            "",
            "## Executive Summary",
            self.executive_summary,
            "",
            "## Problem Areas",
        ]

        for i, problem in enumerate(self.problem_areas, 1):
            lines.extend([
                f"### {i}. {problem.category.title()} - {problem.severity.value.upper()}",
                problem.description,
                "",
                "**Recommendations:**",
            ])
            for rec in problem.recommendations:
                lines.append(f"- {rec}")
            lines.append("")

        lines.extend([
            "## Detailed Analysis",
            "",
            "### Jira Metrics",
            self.jira_summary,
            "",
            "### Test Quality (Zephyr)",
            self.zephyr_summary,
            "",
            "### Incidents",
            self.incident_summary,
        ])

        return "\n".join(lines)
