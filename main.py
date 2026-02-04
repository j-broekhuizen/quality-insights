#!/usr/bin/env python3
"""Quality Insights Agent - Main entry point."""

import os
import sys
import uuid
from dotenv import load_dotenv
from deepagents import create_deep_agent, SubAgent
from langchain_core.messages import HumanMessage, AIMessage
from rich.console import Console
from rich.status import Status

from src.tools.jira_tools import get_sprint_metrics, get_velocity_trend, get_tickets_by_priority
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
        description="Analyzes Jira sprint data, velocity trends, delivery metrics, and ticket priorities to identify development bottlenecks and planning issues",
        model=MODEL,
        tools=[get_sprint_metrics, get_velocity_trend, get_tickets_by_priority],
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


def interactive_mode():
    """Run the Quality Insights Agent in interactive CLI mode."""
    console = Console()

    console.print("=" * 60)
    console.print("Quality Insights Agent - Interactive Mode")
    console.print("=" * 60)
    console.print()
    console.print("Initializing agent...")

    agent = create_quality_insights_agent()

    console.print()
    console.print("Available subagents:")
    console.print("  • jira_analyst     - Sprint and velocity analysis")
    console.print("  • zephyr_analyst   - Test quality and pass rate analysis")
    console.print("  • incident_analyst - Incident trend and MTTR analysis")
    console.print("  • validator        - Report quality validation")
    console.print()
    console.print("Example prompts:")
    console.print("  • Generate a quality report for the team")
    console.print("  • What are the top quality issues we should address?")
    console.print("  • Analyze our sprint velocity and test quality trends")
    console.print()
    console.print("Type 'exit' or 'quit' to end the session.")
    console.print("=" * 60)
    console.print()

    # Track conversation history using LangChain message objects
    conversation_history = []

    # Create a unique thread ID for this session
    thread_id = f"quality-insights-{uuid.uuid4().hex[:8]}"
    console.print(f"[dim]Thread ID: {thread_id}[/dim]\n")

    while True:
        try:
            # Get user input
            user_input = input("\n\033[1;36mYou:\033[0m ").strip()

            # Check for exit commands
            if user_input.lower() in ["exit", "quit", "q"]:
                console.print("\nGoodbye!")
                break

            # Skip empty inputs
            if not user_input:
                continue

            # Add user message to history
            conversation_history.append(HumanMessage(content=user_input))

            # Stream the agent response with a spinner
            try:
                response_content = ""
                is_streaming = False
                status = None

                # Start with thinking spinner
                status = Status("[bold green]Thinking...", spinner="dots", console=console)
                status.start()

                try:
                    # Use astream_events for better streaming with thread tracking
                    import asyncio

                    async def stream_response():
                        nonlocal response_content, is_streaming, status

                        async for event in agent.astream_events(
                            {"messages": conversation_history},
                            config={"configurable": {"thread_id": thread_id}},
                            version="v2",
                        ):
                            event_type = event.get("event")

                            # When we get streaming tokens from the model
                            if event_type == "on_chat_model_stream":
                                chunk = event.get("data", {}).get("chunk")
                                if chunk and hasattr(chunk, "content") and chunk.content:
                                    # Extract text from content (may be string or list of blocks)
                                    content = chunk.content
                                    if isinstance(content, list):
                                        # Extract text from content blocks
                                        text = "".join(
                                            block.get("text", "")
                                            for block in content
                                            if isinstance(block, dict)
                                            and block.get("type") == "text"
                                        )
                                    else:
                                        text = content

                                    if text:
                                        # Stop the spinner when we start streaming text
                                        if not is_streaming:
                                            if status:
                                                status.stop()
                                                status = None
                                            console.print()
                                            console.print("[bold green]Agent:[/bold green] ", end="")
                                            is_streaming = True

                                        # Print the token
                                        print(text, end="", flush=True)
                                        response_content += text

                    # Run the async streaming
                    asyncio.run(stream_response())

                finally:
                    # Ensure spinner is stopped
                    if status:
                        status.stop()

                # Print newline after streaming completes
                if is_streaming:
                    console.print("\n")

                # Add assistant response to history
                if response_content:
                    conversation_history.append(AIMessage(content=response_content))
                else:
                    console.print("\n(No response content)")

            except Exception as e:
                console.print(f"\n[bold red]Error during agent execution:[/bold red] {e}")
                import traceback
                traceback.print_exc()
                # Remove the last user message since we couldn't process it
                if conversation_history and len(conversation_history) > 0:
                    conversation_history.pop()

        except KeyboardInterrupt:
            console.print("\n\nSession interrupted. Goodbye!")
            break
        except EOFError:
            console.print("\n\nGoodbye!")
            break


if __name__ == "__main__":
    # Check if running in interactive mode
    if len(sys.argv) > 1 and sys.argv[1] in ["-i", "--interactive"]:
        interactive_mode()
    else:
        # Default: Show info and instructions
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
        print("Usage options:")
        print("  1. Interactive CLI:  python main.py -i")
        print("  2. LangGraph Studio: langgraph dev")
        print()
        print("Example prompts:")
        print("  • Generate a quality report for the team")
        print("  • What are the top quality issues we should address?")
        print("  • Analyze our sprint velocity and test quality trends")
        print()
        print("=" * 60)
