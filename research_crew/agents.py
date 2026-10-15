"""Small, transparent workflow stages for the research demo."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any


@dataclass
class Review:
    passed: bool
    notes: list[str]


def plan_research(question: str, max_queries: int = 3) -> list[str]:
    """Create focused search queries from a research question.

    This is a deterministic baseline planner, not an LLM.
    """
    cleaned = re.sub(r"\s+", " ", question).strip().rstrip("?!.")
    if not cleaned:
        raise ValueError("Please provide a non-empty research question.")

    queries = [cleaned]
    # Add targeted angles without pretending these are model-generated.
    if len(cleaned.split()) >= 4 and max_queries >= 2:
        queries.append(f"{cleaned} benefits limitations")
    if len(cleaned.split()) >= 4 and max_queries >= 3:
        queries.append(f"{cleaned} examples practical applications")

    unique: list[str] = []
    for query in queries:
        if query.lower() not in {item.lower() for item in unique}:
            unique.append(query)
    return unique[:max_queries]


def write_report(question: str, results: list[dict[str, Any]]) -> str:
    """Turn search results into a structured evidence-first draft."""
    if not results:
        return (
            f"# Research report: {question}\n\n"
            "## Findings\n\nNo search results were returned. "
            "Check network access and try a narrower query.\n"
        )

    lines = [
        f"# Research report: {question}",
        "",
        "## Summary of retrieved material",
        "",
        "The items below are search-result summaries, not independently verified facts. "
        "Open the source links to confirm details before relying on them.",
        "",
    ]
    for index, item in enumerate(results, start=1):
        title = str(item.get("title") or "Untitled result").strip()
        body = str(item.get("body") or "No snippet was provided.").strip()
        url = str(item.get("url") or "").strip()
        lines.extend([f"### {index}. {title}", "", body, ""])
        if url:
            lines.append(f"Source: {url}")
            lines.append("")

    lines.extend([
        "## Conclusion",
        "",
        "Use the linked pages to compare the evidence and identify agreement or disagreement. "
        "This demo does not automatically establish that a claim is true.",
        "",
    ])
    return "\n".join(lines)


def review_report(report: str, results: list[dict[str, Any]]) -> Review:
    """Run basic quality checks; this is not a semantic fact-checker."""
    notes: list[str] = []
    if not results:
        notes.append("No search results were retrieved.")
    if "Source:" not in report:
        notes.append("No source links were included in the report.")
    if len(results) < 3:
        notes.append("Fewer than three results were retrieved; consider another search.")
    if "## Conclusion" not in report:
        notes.append("The report is missing a conclusion section.")
    if not notes:
        notes.append("Basic structure and source-link checks passed; claims still need manual verification.")
    passed = bool(results) and "Source:" in report and "## Conclusion" in report
    return Review(passed=passed, notes=notes)
