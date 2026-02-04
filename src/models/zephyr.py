"""Pydantic models for Zephyr test execution data."""

from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class TestStatus(str, Enum):
    """Test execution status."""
    PASSED = "passed"
    FAILED = "failed"
    BLOCKED = "blocked"
    SKIPPED = "skipped"


class TestExecution(BaseModel):
    """Represents a single test execution."""
    test_id: str = Field(..., description="Unique test identifier")
    test_name: str = Field(..., description="Human-readable test name")
    status: TestStatus = Field(..., description="Execution result status")
    executed_at: datetime = Field(..., description="Execution timestamp")
    duration_seconds: float = Field(..., ge=0, description="Test duration in seconds")
    cycle: str = Field(..., description="Test cycle name")

    @property
    def passed(self) -> bool:
        """Check if test passed."""
        return self.status == TestStatus.PASSED


class TestCycleMetrics(BaseModel):
    """Aggregated metrics for a test cycle."""
    cycle_name: str = Field(..., description="Test cycle identifier")
    start_date: str = Field(..., description="Cycle start date (YYYY-MM-DD)")
    end_date: str = Field(..., description="Cycle end date (YYYY-MM-DD)")
    executions: list[TestExecution] = Field(default_factory=list, description="Test executions in cycle")

    @property
    def total_tests(self) -> int:
        """Total number of test executions."""
        return len(self.executions)

    @property
    def passed(self) -> int:
        """Number of passed tests."""
        return sum(1 for test in self.executions if test.status == TestStatus.PASSED)

    @property
    def failed(self) -> int:
        """Number of failed tests."""
        return sum(1 for test in self.executions if test.status == TestStatus.FAILED)

    @property
    def blocked(self) -> int:
        """Number of blocked tests."""
        return sum(1 for test in self.executions if test.status == TestStatus.BLOCKED)

    @property
    def skipped(self) -> int:
        """Number of skipped tests."""
        return sum(1 for test in self.executions if test.status == TestStatus.SKIPPED)

    @property
    def pass_rate(self) -> float:
        """Calculate test pass rate percentage."""
        if self.total_tests == 0:
            return 0.0
        return round((self.passed / self.total_tests) * 100, 2)

    @property
    def pass_rate_str(self) -> str:
        """Human-readable pass rate."""
        return f"{self.pass_rate}%"
