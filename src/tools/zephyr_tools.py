"""Zephyr test quality analysis tools."""

from collections import defaultdict
from langchain_core.tools import tool
from ..data.mock_data import load_zephyr_data


@tool
def get_test_pass_rate(cycle_name: str | None = None) -> dict:
    """Get test pass rate for a test cycle.

    Args:
        cycle_name: Optional cycle name (e.g., 'Regression-Dec-Week4').
                   If None, returns pass rate for the most recent cycle.

    Returns:
        Dictionary with test pass rate metrics including:
        - cycle_name: Name of the test cycle
        - total_tests: Total number of test executions
        - passed: Number of passed tests
        - failed: Number of failed tests
        - blocked: Number of blocked tests
        - skipped: Number of skipped tests
        - pass_rate: Pass rate percentage
        - date_range: Cycle start and end dates
    """
    data = load_zephyr_data()
    cycles = data["test_cycles"]

    # Get specific cycle or latest
    if cycle_name:
        cycle = next((c for c in cycles if c["cycle_name"] == cycle_name), None)
        if not cycle:
            return {"error": f"Test cycle '{cycle_name}' not found"}
    else:
        cycle = cycles[-1]  # Latest cycle

    # Calculate metrics
    executions = cycle["executions"]
    total = len(executions)
    passed = sum(1 for e in executions if e["status"] == "passed")
    failed = sum(1 for e in executions if e["status"] == "failed")
    blocked = sum(1 for e in executions if e["status"] == "blocked")
    skipped = sum(1 for e in executions if e["status"] == "skipped")

    pass_rate = (passed / total * 100) if total > 0 else 0.0

    return {
        "cycle_name": cycle["cycle_name"],
        "total_tests": total,
        "passed": passed,
        "failed": failed,
        "blocked": blocked,
        "skipped": skipped,
        "pass_rate": round(pass_rate, 2),
        "date_range": f"{cycle['start_date']} to {cycle['end_date']}",
    }


@tool
def get_flaky_tests(threshold: float = 0.7, min_executions: int = 3) -> dict:
    """Identify flaky tests with inconsistent results across test cycles.

    A test is considered flaky if its pass rate is below the threshold
    and it has been executed multiple times with varying results.

    Args:
        threshold: Pass rate threshold below which tests are considered flaky (default: 0.7).
        min_executions: Minimum number of executions required to consider a test (default: 3).

    Returns:
        Dictionary with flaky test analysis including:
        - flaky_tests: List of flaky tests with their pass rates
        - total_flaky_tests: Count of flaky tests identified
        - analysis_period: Description of analysis scope
    """
    data = load_zephyr_data()
    cycles = data["test_cycles"]

    # Track test execution results across all cycles
    test_results = defaultdict(lambda: {"passed": 0, "total": 0, "test_name": ""})

    for cycle in cycles:
        for execution in cycle["executions"]:
            test_id = execution["test_id"]
            test_results[test_id]["test_name"] = execution["test_name"]
            test_results[test_id]["total"] += 1
            if execution["status"] == "passed":
                test_results[test_id]["passed"] += 1

    # Identify flaky tests
    flaky_tests = []
    for test_id, results in test_results.items():
        if results["total"] >= min_executions:
            pass_rate = (
                results["passed"] / results["total"] if results["total"] > 0 else 0.0
            )
            # Flaky if pass rate is between 0 and threshold (not always failing or passing)
            if 0 < pass_rate < threshold:
                flaky_tests.append(
                    {
                        "test_id": test_id,
                        "test_name": results["test_name"],
                        "executions": results["total"],
                        "passed": results["passed"],
                        "failed": results["total"] - results["passed"],
                        "pass_rate": round(pass_rate * 100, 2),
                    }
                )

    # Sort by pass rate (lowest first)
    flaky_tests.sort(key=lambda x: x["pass_rate"])

    return {
        "flaky_tests": flaky_tests,
        "total_flaky_tests": len(flaky_tests),
        "threshold": threshold,
        "min_executions": min_executions,
        "analysis_period": f"Analyzed {len(cycles)} test cycles",
    }
