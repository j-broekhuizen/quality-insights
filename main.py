#!/usr/bin/env python3
"""Quality Insights Agent - Main entry point."""

import os
from dotenv import load_dotenv
from deepagents import create_deep_agent, SubAgent

from src.tools.jira_tools import get_sprint_metrics, get_velocity_trend
from src.tools.zephyr_tools import get_test_pass_rate, get_flaky_tests
from src.tools.incident_tools import get_incident_summary, get_mttr_by_severity
from src.tools.validator_tools import validate_report_format, check_report_quality
from src.prompts import (
    MAIN_AGENT_PROMPT,
    JIRA_AGENT_PROMPT,
    ZEPHYR_AGENT_PROMPT,
    INCIDENT_AGENT_PROMPT,
    VALIDATOR_AGENT_PROMPT,
)

# Load environment variables
load_dotenv()

# Model configuration
MODEL = os.getenv("MODEL", "anthropic:claude-sonnet-4-5-20250929")


def create_quality_insights_agent():
    """Create the Quality Insights multi-agent system.

    The system consists of:
    - Main coordinator agent that orchestrates analysis and synthesis
    - Jira analyst sub-agent for sprint metrics and velocity analysis
    - Zephyr analyst sub-agent for test quality and pass rate analysis
    - Incident analyst sub-agent for incident trends and MTTR analysis
    - Validator sub-agent for report quality assurance

    Returns:
        Configured deep agent instance ready for use
    """

    # Jira Analysis Subagent
    jira_agent = SubAgent(
        name="jira_analyst",
        description="Analyzes Jira sprint data, velocity trends, and delivery metrics to identify development bottlenecks and planning issues",
        model=MODEL,
        tools=[get_sprint_metrics, get_velocity_trend],
        system_prompt=JIRA_AGENT_PROMPT,
    )

    # Zephyr Test Analysis Subagent
    zephyr_agent = SubAgent(
        name="zephyr_analyst",
        description="Analyzes test execution data, pass rates, and test quality metrics to identify quality trends and flaky tests",
        model=MODEL,
        tools=[get_test_pass_rate, get_flaky_tests],
        system_prompt=ZEPHYR_AGENT_PROMPT,
    )

    # Incident Analysis Subagent
    incident_agent = SubAgent(
        name="incident_analyst",
        description="Analyzes incident trends, severity distribution, and MTTR metrics to identify reliability issues and recurring problems",
        model=MODEL,
        tools=[get_incident_summary, get_mttr_by_severity],
        system_prompt=INCIDENT_AGENT_PROMPT,
    )

    # Validator Subagent
    validator_agent = SubAgent(
        name="validator",
        description="Validates quality report completeness, accuracy, and actionability to ensure executive-ready output",
        model=MODEL,
        tools=[validate_report_format, check_report_quality],
        system_prompt=VALIDATOR_AGENT_PROMPT,
    )

    # Main coordinating agent
    agent = create_deep_agent(
        model=MODEL,
        subagents=[jira_agent, zephyr_agent, incident_agent, validator_agent],
        system_prompt=MAIN_AGENT_PROMPT,
    )

    return agent


if __name__ == "__main__":
    print("=" * 60)
    print("Quality Insights Agent - Demo")
    print("=" * 60)
    print()

    agent = create_quality_insights_agent()

    print("Quality Insights Agent created successfully!")
    print()
    print("Available subagents:")
    print("  • jira_analyst     - Sprint and velocity analysis")
    print("  • zephyr_analyst   - Test quality and pass rate analysis")
    print("  • incident_analyst - Incident trend and MTTR analysis")
    print("  • validator        - Report quality validation")
    print()
    print("To use this agent:")
    print("  1. Run 'langgraph dev' to start LangGraph Studio")
    print("  2. Try prompts like:")
    print("     - 'Generate a quality report for the team'")
    print("     - 'What are the top quality issues we should address?'")
    print("     - 'Analyze our sprint velocity and test quality trends'")
    print()
    print("=" * 60)
