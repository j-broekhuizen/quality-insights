# Quality Insights - Multi-Agent Demo

A production-ready demo showcasing a multi-agent quality analysis system using LangChain's DeepAgents framework. The system analyzes quality metrics from Jira, Zephyr, and incident tracking to generate executive-level insights and recommendations.

## Overview

This demo illustrates the conversation with LangChain (from the January 29, 2026 call) where a quality insights system was discussed for analyzing team performance across multiple data sources. The agent orchestrates specialized sub-agents to analyze sprint velocity, test quality, and incident trends, then synthesizes findings into actionable executive summaries.

## Features

- **Multi-Agent Architecture**: Coordinator agent delegates to specialized analysts
- **Parallel Execution**: Jira, Zephyr, and Incident agents run concurrently
- **Quality Validation**: Built-in validator ensures report completeness and accuracy
- **Rich Mock Data**: 3 months of realistic sprint, test, and incident data
- **Executive-Ready Output**: Concise summaries with specific metrics and recommendations

## Architecture

```
Main Agent (Quality Insights Coordinator)
├── Jira Agent → Analyzes sprint metrics, velocity trends, delivery bottlenecks
├── Zephyr Agent → Analyzes test pass rates, flaky tests, quality trends
├── Incident Agent → Analyzes incident frequency, MTTR, severity distribution
└── Validator Agent → Validates report format, completeness, and quality
```

**Execution Flow:**
1. User requests quality insights
2. Main agent delegates to Jira, Zephyr, and Incident agents in parallel
3. Each specialist agent analyzes its domain and returns findings
4. Main agent synthesizes all analyses into executive summary
5. Validator agent checks report quality and completeness
6. Final report includes problem areas with recommendations

## Setup

### Prerequisites

- Python 3.11 or higher
- uv (recommended) or pip
- Anthropic API key
- LangSmith API key (optional, for tracing)

### Installation

1. Clone the repository and navigate to the demo:
   ```bash
   cd demos/quality-insights
   ```

2. Install dependencies:
   ```bash
   uv sync
   ```

3. Configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys
   ```

4. Set up your `.env` file:
   ```bash
   MODEL=anthropic:claude-sonnet-4-5-20250929
   ANTHROPIC_API_KEY=sk-ant-...
   LANGSMITH_API_KEY=lsv2_pt_...
   LANGSMITH_PROJECT=quality-insights
   LANGSMITH_TRACING=true
   ```

## Usage

### Option 1: LangGraph Studio (Recommended)

Run the agent with LangGraph Studio for visual debugging and testing:

```bash
langgraph dev
```

Then open LangGraph Studio and try prompts like:
- "Generate a quality report for the team"
- "What are the top 3 quality issues we should address?"
- "Analyze our sprint velocity and test quality trends"
- "Summarize our incident trends and identify problem areas"

### Option 2: Python Script

Run the agent directly:

```bash
python main.py
```

### Option 3: Programmatic Usage

```python
from main import create_quality_insights_agent

agent = create_quality_insights_agent()

# Generate a quality report
response = agent.invoke({
    "messages": [{
        "role": "user",
        "content": "Generate a quality report for the Quality Insights team"
    }]
})

print(response)
```

## Available Tools

### Jira Analysis Tools

| Tool | Description |
|------|-------------|
| `get_sprint_metrics` | Get metrics for a specific sprint including velocity, completion rate, and ticket breakdown |
| `get_velocity_trend` | Analyze velocity trends over recent sprints to identify improving or declining patterns |

### Zephyr Test Tools

| Tool | Description |
|------|-------------|
| `get_test_pass_rate` | Get pass rate metrics for a test cycle including passed, failed, blocked tests |
| `get_flaky_tests` | Identify flaky tests with inconsistent results across multiple executions |

### Incident Tools

| Tool | Description |
|------|-------------|
| `get_incident_summary` | Get incident summary for a time period with severity breakdown and affected users |
| `get_mttr_by_severity` | Calculate mean time to resolve (MTTR) by incident severity level |

### Validation Tools

| Tool | Description |
|------|-------------|
| `validate_report_format` | Check that report has all required sections and proper structure |
| `check_report_quality` | Assess report quality, actionability, and completeness with scoring |

## Mock Data

The demo includes realistic mock data covering 3 months (October-December 2024):

### Jira Data
- 6 sprints with varying velocities (72-96% completion)
- 45+ tickets across different statuses
- Realistic sprint planning and delivery patterns
- Some sprints with blockers and incomplete work

### Zephyr Data
- 12 test cycles (weekly regression cycles)
- 10-15 tests per cycle with varying pass rates
- Intentional test failures to demonstrate quality issues
- Flaky test patterns for reliability analysis

### Incident Data
- 23 incidents across all severity levels
- Mix of resolved and unresolved incidents
- Realistic MTTR by severity (critical: ~6.5 hours)
- Common root causes (database, memory, configuration)

## Project Structure

```
quality-insights/
├── main.py                     # Main entry point
├── graph.py                    # LangGraph export
├── pyproject.toml             # Dependencies
├── .env.example               # Environment template
├── README.md                  # This file
├── AGENTS.md                  # Agent behavior guidelines
├── CLAUDE.md                  # Claude Code instructions
├── src/
│   ├── models/                # Pydantic data models
│   │   ├── jira.py           # Sprint and ticket models
│   │   ├── zephyr.py         # Test execution models
│   │   ├── incident.py       # Incident and severity models
│   │   └── report.py         # Report output models
│   ├── tools/                 # LangChain tools
│   │   ├── jira_tools.py     # Sprint metrics, velocity trends
│   │   ├── zephyr_tools.py   # Pass rates, flaky tests
│   │   ├── incident_tools.py # Incident summary, MTTR
│   │   └── validator_tools.py # Format and quality validation
│   ├── data/                  # Mock data and loaders
│   │   ├── jira_data.json    # 6 sprints of mock data
│   │   ├── zephyr_data.json  # 12 test cycles
│   │   ├── incident_data.json # 23 incidents
│   │   └── mock_data.py      # Data loading functions
│   └── prompts.py            # Agent system prompts
└── tests/
    └── test_agents.py        # Basic tests
```

## Example Output

When you ask "Generate a quality report for the team", the agent will:

1. **Jira Analysis**: Identify velocity trends, sprint completion rates, blockers
2. **Zephyr Analysis**: Report test pass rates, identify flaky tests, quality trends
3. **Incident Analysis**: Summarize incident frequency, MTTR, severity distribution
4. **Synthesis**: Combine findings into executive summary with top problem areas
5. **Validation**: Check report completeness and quality
6. **Final Report**: Executive summary with 3-5 prioritized problem areas

Sample output snippet:
```
Executive Summary:

The Quality Insights team is experiencing three critical quality concerns requiring
immediate attention. Sprint velocity declined 23% in Sprint 2024-11-1, dropping to
72.9% completion rate. Test quality deteriorated with pass rates falling to 83.33%
in Regression-Nov-Week1. Production incidents spiked with 2 critical incidents
affecting over 3,000 users combined.

Problem Areas:

1. Sprint Velocity Decline (HIGH)
   - Sprint 2024-11-1 completed only 35 of 48 planned points (72.9%)
   - 2 blocked tickets, 3 incomplete tickets suggest planning issues
   Recommendations:
   - Review sprint planning process for accuracy
   - Investigate root causes of blocked tickets
   - Consider reducing sprint capacity until velocity stabilizes

2. Test Quality Degradation (CRITICAL)
   - Regression-Nov-Week1 pass rate: 83.33% (10/12 tests passed)
   - Critical failures: Password reset flow, Dashboard metrics loading
   - Flaky test TEST-004 with 66.67% pass rate
   Recommendations:
   - Fix critical test failures immediately
   - Investigate and stabilize TEST-004
   - Add test reliability monitoring

...
```

## Customization

### Adding New Data Sources

1. Create a new model in `src/models/`
2. Add mock data JSON file in `src/data/`
3. Implement tools in `src/tools/`
4. Create agent prompt in `src/prompts.py`
5. Add sub-agent to `main.py`

### Replacing Mock Data

To connect to real data sources:

1. Update `src/data/mock_data.py` to call real APIs
2. Modify tool implementations to use real data loaders
3. Update data models if needed for real schemas
4. Add authentication and error handling

### Adjusting Agent Behavior

Edit `src/prompts.py` to modify agent personalities and priorities:
- Change analysis focus areas
- Adjust severity thresholds
- Modify report format and tone
- Add domain-specific expertise

## Troubleshooting

### Agent not finding data
- Verify mock JSON files exist in `src/data/`
- Check that data loaders in `mock_data.py` have correct paths

### Tools not being called
- Review agent prompts in `src/prompts.py`
- Ensure tool descriptions are clear and relevant
- Check that tools are properly registered in `main.py`

### Poor quality reports
- Adjust validator thresholds in `validator_tools.py`
- Enhance agent prompts with more specific instructions
- Add more examples to system prompts

### API errors
- Verify `.env` file has correct API keys
- Check MODEL setting matches available models
- Ensure sufficient API rate limits

### Viewing LangSmith Traces

To inspect what happened during an agent run:

```bash
uv run langsmith-fetch traces
```

This will fetch recent traces from LangSmith and show you:
- Which tools were called
- Agent reasoning and decisions
- Errors or issues
- Performance metrics

Make sure your `.env` file has:
- `LANGSMITH_API_KEY` set
- `LANGSMITH_TRACING=true`
- `LANGSMITH_PROJECT=quality-insights`

## Contributing

This is a demo project. To extend it:

1. Fork the repository
2. Add new features or data sources
3. Update documentation
4. Test with `langgraph dev`
5. Submit pull request

## License

This demo is part of the LangChain support materials and follows the same license as the main repository.

## Support

For questions or issues:
- Review the [AGENTS.md](AGENTS.md) file for agent behavior details
- Check [CLAUDE.md](CLAUDE.md) for Claude Code integration
- Open an issue in the main repository

## Acknowledgments

This demo is based on the LangChain + Chime call on January 29, 2026, where the quality insights use case was discussed. It demonstrates best practices for:
- Multi-agent orchestration with DeepAgents
- Parallel agent execution
- Report validation and quality assurance
- Executive-level insight generation
