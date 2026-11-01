"""Research workflow stages with optional LLM assistance and deterministic fallback."""
from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any

from openai import OpenAI


@dataclass
class Review:
    passed: bool
    notes: list[str]


def _client() -> OpenAI | None:
    """Return an OpenAI-compatible client when credentials are configured."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    kwargs: dict[str, Any] = {"api_key": api_key}
    base_url = os.getenv("LLM_BASE_URL")
    if base_url:
        kwargs["base_url"] = base_url
    return OpenAI(**kwargs)


def _model() -> str:
    return os.getenv("LLM_MODEL", "gpt-4o-mini")


def plan_research(question: str, max_queries: int = 3) -> list[str]:
    """Use an LLM to propose focused queries; fall back to transparent rules."""
    cleaned = re.sub(r"\\s+", " ", question).strip().rstrip("?!.")
    if not cleaned:
        raise ValueError("Please provide a non-empty research question.")

    client = _client()
    if client:
        try:
            response = client.chat.completions.create(
                model=_model(),
                temperature=0.2,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": "Create concise web research queries. Return JSON with a string array field named queries. Do not answer the question."},
                    {"role": "user", "content": f"Research question: {cleaned}\\nReturn at most {max_queries} distinct queries."},
                ],
            )
            data = json.loads(response.choices[0].message.content or "{}")
            queries = [str(q).strip() for q in data.get("queries", []) if str(q).strip()]
            if queries:
                return list(dict.fromkeys(queries))[:max_queries]
        except Exception as exc:
            print(f"[Planner] LLM unavailable ({type(exc).__name__}); using deterministic planning.")

    queries = [cleaned]
    if len(cleaned.split()) >= 4 and max_queries >= 2:
        queries.append(f"{cleaned} benefits limitations")
    if len(cleaned.split()) >= 4 and max_queries >= 3:
        queries.append(f"{cleaned} examples practical applications")
    return list(dict.fromkeys(queries))[:max_queries]


def write_report(question: str, results: list[dict[str, Any]]) -> str:
    """Synthesize retrieved snippets with an LLM, retaining source links."""
    if not results:
        return f"# Research report: {question}\\n\\n## Findings\\n\\nNo search results were returned. Check network access and try a narrower query.\\n"

    client = _client()
    if client:
        evidence = [
            {"title": str(item.get("title") or ""), "snippet": str(item.get("body") or ""),
             "url": str(item.get("url") or "")}
            for item in results
        ]
        try:
            response = client.chat.completions.create(
                model=_model(),
                temperature=0.2,
                messages=[
                    {"role": "system", "content": (
                        "You are an evidence-grounded research writer. Use only the supplied search snippets. "
                        "Do not invent facts, statistics, quotations, or sources. Clearly state when evidence is "
                        "insufficient or conflicting. Cite claims inline using [1], [2], etc., matching the "
                        "numbered source list. Distinguish source claims from your synthesis."
                    )},
                    {"role": "user", "content": (
                        f"Research question: {question}\\n\\nEvidence (JSON): "
                        f"{json.dumps(evidence, ensure_ascii=False)}\\n\\n"
                        "Write Markdown with Summary, Key findings, Limitations/uncertainties, and Conclusion."
                    )},
                ],
            )
            draft = (response.choices[0].message.content or "").strip()
            if draft:
                source_lines = ["\\n## Sources\\n"]
                for index, item in enumerate(results, start=1):
                    url = str(item.get("url") or "").strip()
                    title = str(item.get("title") or "Untitled result").strip()
                    if url:
                        source_lines.append(f"{index}. [{title}]({url})")
                return f"# Research report: {question}\\n\\n{draft}\\n" + "\\n".join(source_lines) + "\\n"
        except Exception as exc:
            print(f"[Writer] LLM unavailable ({type(exc).__name__}); using evidence-list fallback.")

    lines = [f"# Research report: {question}", "", "## Summary of retrieved material", "",
             "These are search-result summaries, not independently verified facts. Verify claims at the linked sources.", ""]
    for index, item in enumerate(results, start=1):
        title = str(item.get("title") or "Untitled result").strip()
        body = str(item.get("body") or "No snippet was provided.").strip()
        url = str(item.get("url") or "").strip()
        lines.extend([f"### {index}. {title}", "", body, ""])
        if url:
            lines.extend([f"Source: {url}", ""])
    lines.extend(["## Conclusion", "", "Compare the linked sources and verify important claims independently.", ""])
    return "\\n".join(lines)


def review_report(report: str, results: list[dict[str, Any]]) -> Review:
    """Combine deterministic checks with an optional LLM critique (not fact verification)."""
    notes: list[str] = []
    if not results:
        notes.append("No search results were retrieved.")
    if "Source:" not in report and "## Sources" not in report:
        notes.append("No source links were included in the report.")
    if len(results) < 3:
        notes.append("Fewer than three results were retrieved; consider another search.")
    if "## Conclusion" not in report:
        notes.append("The report is missing a conclusion section.")

    client = _client()
    if client and results:
        try:
            response = client.chat.completions.create(
                model=_model(), temperature=0,
                messages=[
                    {"role": "system", "content": "Review this research draft for unsupported specifics, missing/unclear citations, and whether it answers the question. Do not claim to verify facts against the internet. Return at most 4 concise actionable bullet points; if none, say 'No additional issues found.'"},
                    {"role": "user", "content": report[:12000]},
                ],
            )
            critique = (response.choices[0].message.content or "").strip()
            if critique and "no additional issues found" not in critique.lower():
                notes.append("LLM critique: " + critique.replace("\\n", " "))
        except Exception as exc:
            notes.append(f"LLM review unavailable ({type(exc).__name__}); deterministic checks only.")

    if not notes:
        notes.append("Structural checks passed; claims still require human/source verification.")
    passed = bool(results) and ("Source:" in report or "## Sources" in report) and "## Conclusion" in report
    return Review(passed=passed, notes=notes)
