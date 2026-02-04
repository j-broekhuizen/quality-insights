# Claude Code Integration Guide

This document provides guidance for working with the Quality Insights demo using Claude Code.

## Project Overview

This is a **demo project** showcasing a multi-agent quality analysis system built with:
- **DeepAgents**: LangChain's framework for multi-agent orchestration
- **4 Sub-Agents**: Jira, Zephyr, Incident, and Validator specialists
- **Mock Data**: 3 months of realistic quality metrics
- **LangGraph Studio**: Visual debugging and testing interface

## LangSmith Integration

**CRITICAL**: When the user asks about traces, runs, or "what happened", ALWAYS use langsmith-fetch FIRST.

Common triggers:
- "What happened in the most recent trace?"
- "Show me the latest run"
- "What did the agent do?"
- "Check the trace"
- Any question about LangSmith traces or runs

**Action**: Immediately run:
```bash
uv run langsmith-fetch traces
```

Do NOT search for trace files in the filesystem or try other methods. Use langsmith-fetch.

To add the tool to the project (if not already installed):
```bash
uv add langsmith-fetch
```

## Development Workflow

### Making Changes

When modifying this demo, follow these priorities:

1. **Agent Prompts** (`src/prompts.py`)
   - Most impactful changes
   - Controls agent behavior and expertise
   - Test after changes with `langgraph dev`

2. **Tools** (`src/tools/`)
   - Modify tool logic and data processing
   - Keep tool descriptions clear and specific
   - Ensure return types match documented schemas

3. **Mock Data** (`src/data/*.json`)
   - Adjust to demonstrate different scenarios
   - Maintain realistic patterns
   - Update data loaders if schema changes

4. **Models** (`src/models/`)
   - Change only if data structure evolves
   - Keep models aligned with JSON schemas
   - Update tools if model properties change

### Testing Changes

After making changes:

```bash
# Option 1: Test with LangGraph Studio
langgraph dev

# Option 2: Test programmatically
python main.py

# Option 3: Run basic tests
pytest tests/
```

## Common Tasks

### Adding a New Data Source

If a user asks to add a new data source (e.g., "Add GitHub PR metrics"):

1. **Create the model** in `src/models/`:
   ```python
   # src/models/github.py
   class PullRequest(BaseModel):
       id: str
       title: str
       state: str
       ...
   ```

2. **Add mock data** in `src/data/`:
   ```json
   // src/data/github_data.json
   {
     "pull_requests": [...]
   }
   ```

3. **Create tools** in `src/tools/`:
   ```python
   # src/tools/github_tools.py
   @tool
   def get_pr_metrics() -> dict:
       """Get PR review metrics."""
       ...
   ```

4. **Add agent prompt** in `src/prompts.py`:
   ```python
   GITHUB_AGENT_PROMPT = """You are a GitHub PR analysis specialist..."""
   ```

5. **Register sub-agent** in `main.py`:
   ```python
   github_agent = SubAgent(
       name="github_analyst",
       description="Analyzes PR metrics...",
       tools=[get_pr_metrics],
       system_prompt=GITHUB_AGENT_PROMPT,
   )
   ```

6. **Update documentation** (README.md, AGENTS.md)

### Adjusting Agent Behavior

If reports aren't meeting expectations:

1. **Review agent prompts** in `src/prompts.py`
2. **Add specific examples** of desired output
3. **Adjust validation thresholds** in `src/tools/validator_tools.py`
4. **Test with different queries** to verify improvements

### Debugging Issues

**Agent not calling tools:**
- Check tool descriptions are clear and relevant
- Review agent prompt for tool usage instructions
- Verify tools are registered in sub-agent

**Poor quality output:**
- Strengthen system prompts with more examples
- Adjust validator scoring thresholds
- Add more specific requirements to prompts

**Data not loading:**
- Verify JSON files exist and are valid
- Check data loader paths in `mock_data.py`
- Ensure model schemas match JSON structure

## File Organization

```
quality-insights/
├── main.py                    # Main entry - modify to add sub-agents
├── graph.py                   # LangGraph export - usually no changes needed
├── src/
│   ├── models/               # Data structures - modify when schema changes
│   ├── tools/                # Analysis logic - modify for new functionality
│   ├── data/                 # Mock data and loaders - update for new scenarios
│   └── prompts.py           # Agent behavior - most frequent changes here
├── tests/                    # Add tests for new features
├── README.md                 # User-facing documentation
├── AGENTS.md                 # Agent behavior reference
└── CLAUDE.md                 # This file
```

## Best Practices

### When Adding Features

1. Start with the data model
2. Create mock data that demonstrates the feature
3. Implement tools with clear descriptions
4. Write agent prompt with examples
5. Test end-to-end before committing
6. Update documentation

### When Fixing Bugs

1. Identify the affected component (agent, tool, data)
2. Add a test that reproduces the issue
3. Fix the issue
4. Verify the test passes
5. Check for similar issues in related code

### When Refactoring

1. Ensure tests pass before starting
2. Make small, incremental changes
3. Test after each change
4. Update documentation if interfaces change
5. Consider backward compatibility

## LangSmith Integration

This demo supports LangSmith tracing for debugging:

1. Set environment variables in `.env`:
   ```bash
   LANGSMITH_API_KEY=lsv2_pt_...
   LANGSMITH_PROJECT=quality-insights
   LANGSMITH_TRACING=true
   ```

2. Run the agent (traces appear in LangSmith automatically)

3. Review traces to:
   - See which tools were called
   - Inspect agent reasoning
   - Debug unexpected behavior
   - Measure performance

## Common Patterns

### Adding Validation Rules

Edit `src/tools/validator_tools.py`:

```python
# Add new validation check
if "specific_keyword" not in report_lower:
    errors.append("Report must mention specific_keyword")
    score -= 10
```

### Changing Report Format

Edit `MAIN_AGENT_PROMPT` in `src/prompts.py`:

```python
MAIN_AGENT_PROMPT = """
...
Format your final report with:
- New Section Name: Description
- Another Section: Description
...
"""
```

### Adjusting Analysis Period

Edit tools to accept different time ranges:

```python
@tool
def get_incident_summary(days: int = 30) -> dict:
    # Adjust default value or add parameters
    ...
```

## Deployment Notes

This is a **demo project** not intended for production deployment. However, if adapting for production:

1. **Replace mock data** with real API integrations
2. **Add error handling** for API failures
3. **Implement rate limiting** for external services
4. **Add authentication** for sensitive data
5. **Set up monitoring** for agent performance
6. **Add comprehensive tests** beyond demo scope

## Support

For questions about this demo:

1. Review [README.md](README.md) for setup and usage
2. Check [AGENTS.md](AGENTS.md) for agent behavior details
3. Examine existing code for patterns
4. Test changes with `langgraph dev`

## Version History

- v0.1.0 (Initial): Basic multi-agent system with Jira, Zephyr, Incident analysis
- Based on LangChain + Chime call discussion (January 29, 2026)

## Future Enhancements

Potential additions for extending the demo:

- [ ] Cloud spend analysis agent
- [ ] Department/team/squad hierarchy support
- [ ] Historical trend comparisons (MoM, QoQ)
- [ ] Anomaly detection for metrics
- [ ] Automated report scheduling
- [ ] Export formats (PDF, Markdown, JSON)
- [ ] Interactive dashboard visualizations
- [ ] Integration with real data sources

When implementing these, follow the patterns established in the existing code.
