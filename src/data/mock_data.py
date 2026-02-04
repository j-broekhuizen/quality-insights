"""Mock data loaders for quality insights demo."""

import json
from pathlib import Path
from typing import Any

# Get the directory where data files are stored
DATA_DIR = Path(__file__).parent

# Cache loaded data to avoid repeated file I/O
_jira_cache: dict[str, Any] | None = None
_zephyr_cache: dict[str, Any] | None = None
_incident_cache: dict[str, Any] | None = None


def load_jira_data() -> dict[str, Any]:
    """Load Jira sprint data from JSON file.

    Returns:
        Dictionary containing sprint data with tickets, velocity, etc.
    """
    global _jira_cache
    if _jira_cache is None:
        with open(DATA_DIR / "jira_data.json", "r") as f:
            _jira_cache = json.load(f)
    return _jira_cache


def load_zephyr_data() -> dict[str, Any]:
    """Load Zephyr test execution data from JSON file.

    Returns:
        Dictionary containing test cycles and execution results.
    """
    global _zephyr_cache
    if _zephyr_cache is None:
        with open(DATA_DIR / "zephyr_data.json", "r") as f:
            _zephyr_cache = json.load(f)
    return _zephyr_cache


def load_incident_data() -> dict[str, Any]:
    """Load incident tracking data from JSON file.

    Returns:
        Dictionary containing incident reports with severity and resolution data.
    """
    global _incident_cache
    if _incident_cache is None:
        with open(DATA_DIR / "incident_data.json", "r") as f:
            _incident_cache = json.load(f)
    return _incident_cache


def clear_cache() -> None:
    """Clear all cached data. Useful for testing or refreshing data."""
    global _jira_cache, _zephyr_cache, _incident_cache
    _jira_cache = None
    _zephyr_cache = None
    _incident_cache = None
