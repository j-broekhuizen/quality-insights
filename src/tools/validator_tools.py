"""Validation tools for quality report completeness and accuracy."""

from langchain_core.tools import tool


@tool
def validate_report_format(report_text: str) -> dict:
    """Validate that the quality report has all required sections.

    Checks for the presence of key sections and ensures the report
    follows the expected structure.

    Args:
        report_text: The quality report text to validate.

    Returns:
        Dictionary with validation results including:
        - valid: Boolean indicating if report passes validation
        - missing_sections: List of missing required sections
        - errors: List of validation errors found
        - warnings: List of validation warnings
    """
    required_sections = [
        "jira",
        "sprint",
        "velocity",
        "zephyr",
        "test",
        "incident",
        "problem",
        "summary",
    ]

    # Check for required sections (case-insensitive)
    report_lower = report_text.lower()
    missing_sections = []
    for section in required_sections:
        if section not in report_lower:
            missing_sections.append(section)

    errors = []
    warnings = []

    # Check report length
    word_count = len(report_text.split())
    if word_count < 100:
        errors.append("Report is too short (less than 100 words)")
    elif word_count > 2000:
        warnings.append("Report is very long (over 2000 words) - consider condensing")

    # Check for specific data mentions
    if not any(char.isdigit() for char in report_text):
        warnings.append("Report should include specific metrics and numbers")

    # Check for recommendations
    if "recommend" not in report_lower and "suggest" not in report_lower:
        warnings.append("Report should include actionable recommendations")

    # Determine if valid
    valid = len(errors) == 0 and len(missing_sections) == 0

    return {
        "valid": valid,
        "missing_sections": missing_sections,
        "errors": errors,
        "warnings": warnings,
        "word_count": word_count,
    }


@tool
def check_report_quality(report_text: str) -> dict:
    """Check if the report meets quality standards.

    Evaluates the report for clarity, completeness, and actionability.

    Args:
        report_text: The quality report text to check.

    Returns:
        Dictionary with quality check results including:
        - quality_score: Score from 0-100 indicating report quality
        - strengths: List of report strengths
        - improvement_areas: List of areas needing improvement
        - recommendations: Specific recommendations for improvement
    """
    report_lower = report_text.lower()
    strengths = []
    improvement_areas = []
    recommendations = []
    score = 100

    # Check for executive summary
    if "executive summary" in report_lower or "summary" in report_lower:
        strengths.append("Includes executive summary")
    else:
        improvement_areas.append("Missing executive summary")
        recommendations.append("Add an executive summary at the beginning")
        score -= 20

    # Check for specific metrics
    has_percentages = "%" in report_text
    has_numbers = any(word.isdigit() for word in report_text.split())

    if has_percentages and has_numbers:
        strengths.append("Includes specific metrics and data points")
    else:
        improvement_areas.append("Lacks specific metrics")
        recommendations.append("Include specific percentages, counts, and measurements")
        score -= 15

    # Check for problem identification
    problem_keywords = ["problem", "issue", "concern", "decline", "failure"]
    if any(keyword in report_lower for keyword in problem_keywords):
        strengths.append("Identifies specific problems")
    else:
        improvement_areas.append("Doesn't clearly identify problems")
        recommendations.append(
            "Explicitly call out problem areas and quality concerns"
        )
        score -= 15

    # Check for recommendations
    recommendation_keywords = ["recommend", "suggest", "should", "action"]
    if any(keyword in report_lower for keyword in recommendation_keywords):
        strengths.append("Provides actionable recommendations")
    else:
        improvement_areas.append("Lacks actionable recommendations")
        recommendations.append(
            "Add specific recommendations for addressing identified issues"
        )
        score -= 20

    # Check for data source coverage
    sources_mentioned = sum(
        [
            "jira" in report_lower,
            "sprint" in report_lower,
            "zephyr" in report_lower,
            "test" in report_lower,
            "incident" in report_lower,
        ]
    )

    if sources_mentioned >= 3:
        strengths.append("Covers multiple data sources")
    else:
        improvement_areas.append("Limited data source coverage")
        recommendations.append(
            "Ensure analysis covers Jira, Zephyr, and Incident data"
        )
        score -= 15

    # Check report structure
    has_sections = report_text.count("\n\n") >= 2  # Multiple paragraphs/sections
    if has_sections:
        strengths.append("Well-structured with clear sections")
    else:
        improvement_areas.append("Poor structure and organization")
        recommendations.append("Organize report into clear sections")
        score -= 15

    # Ensure score doesn't go below 0
    score = max(0, score)

    return {
        "quality_score": score,
        "grade": _score_to_grade(score),
        "strengths": strengths,
        "improvement_areas": improvement_areas,
        "recommendations": recommendations,
        "passes_quality_check": score >= 70,
    }


def _score_to_grade(score: int) -> str:
    """Convert numeric score to letter grade."""
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    else:
        return "F"
