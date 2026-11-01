"""Run the OWL-MCP Research Crew demo from the command line."""
from __future__ import annotations
import argparse, asyncio, json, os
from typing import Any
from dotenv import load_dotenv
from research_crew.agents import plan_research, review_report, write_report
from research_crew.mcp_client import search_with_mcp
from research_crew.report import save_report

async def run_research(question: str) -> tuple[str, list[dict[str, Any]], list[str]]:
    llm_enabled = bool(os.getenv("OPENAI_API_KEY"))
    print(f"\n[Mode] {'LLM-assisted' if llm_enabled else 'Deterministic fallback'}")
    queries = plan_research(question)
    all_results: list[dict[str, Any]] = []
    seen_urls: set[str] = set()
    print("\n[Planner] Planned queries:")
    for query in queries: print(f"  - {query}")
    for query in queries:
        print(f"\n[Researcher] Calling MCP search tool for: {query}")
        try:
            results = await search_with_mcp(query, max_results=4)
        except Exception as exc:
            print(f"[Researcher] Search failed: {type(exc).__name__}. Continuing.")
            continue
        for result in results:
            url = str(result.get("url", "")).strip()
            identity = url or json.dumps(result, sort_keys=True)
            if identity not in seen_urls:
                seen_urls.add(identity)
                all_results.append(result)
    all_results = all_results[:10]
    print(f"\n[Writer] Preparing report from {len(all_results)} unique result(s).")
    report = write_report(question, all_results)
    print("[Reviewer] Running structural and optional LLM critique.")
    review = review_report(report, all_results)
    report += "\n## Review\n\n"
    report += f"- Basic checks: {'passed' if review.passed else 'needs attention'}\n"
    for note in review.notes: report += f"- {note}\n"
    report += "\n> Automated review assists quality checks; it is not independent fact verification.\n"
    return report, all_results, queries

def main() -> None:
    load_dotenv()
    parser = argparse.ArgumentParser(description="Research with MCP search and optional LLM-assisted stages.")
    parser.add_argument("question", help="Research question to investigate")
    args = parser.parse_args()
    try:
        report, results, queries = asyncio.run(run_research(args.question))
    except KeyboardInterrupt:
        print("\nCancelled.")
        return
    path = save_report(report)
    print("\n" + "=" * 72)
    print(report)
    print("=" * 72)
    print(f"Saved report to: {path}")

if __name__ == "__main__":
    main()
