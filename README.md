# OWL-MCP Research Crew

An educational research workflow inspired by the tool-using ideas in CAMEL-AI OWL. It combines a Planner → Researcher → Writer → Reviewer pipeline with web search exposed as a real tool through the Model Context Protocol (MCP).

> Scope and attribution: This is an independent learning project, not the official OWL framework. LLM-assisted stages are optional and use an OpenAI-compatible chat-completions API when configured.

## What it does

1. Planner: Generates focused web queries using an LLM, with a deterministic fallback.
2. Researcher: Calls a local MCP server over stdio; the server runs DuckDuckGo searches and returns titled results with source URLs.
3. Writer: Synthesizes retrieved snippets into a Markdown report with numbered citations and a source list. Without an API key, it creates an evidence-list report.
4. Reviewer: Runs deterministic completeness checks and, when configured, asks an LLM to critique unsupported specifics and unclear citations. This is not independent fact verification.
5. Output: Saves timestamped Markdown reports under reports/.

## Architecture

    Research question
           |
    LLM Planner (or rule-based fallback)
           |
    Researcher / MCP Client (stdio)
           |
    MCP Search Server ----> DuckDuckGo
           |
    Retrieved snippets + URLs
           |
    LLM Writer (or evidence-list fallback)
           |
    Structural checks + optional LLM critique
           |
    Cited Markdown report

## Setup

Python 3.10+ is required.

    git clone https://github.com/ashishmahapatro17-lab/OWL-MCP-Research-Crew.git
    cd OWL-MCP-Research-Crew
    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    cp .env.example .env

On Windows, activate with .venv\Scripts\activate and copy .env.example to .env.

Edit .env and set OPENAI_API_KEY. The default model is gpt-4o-mini. Optionally set LLM_MODEL and LLM_BASE_URL for another compatible provider. Keep .env private; never commit API keys.

Run without an LLM key (deterministic fallback):

    python main.py "How is MCP used to connect AI applications to tools?"

Run with an LLM key configured in .env:

    python main.py "Compare practical uses and limitations of retrieval-augmented generation"

The application prints which mode is active and saves the report under reports/.

## MCP integration

The local server exposes a search_web tool. The client starts it as a subprocess over stdio, initializes an MCP session, discovers the tool, and invokes it. This keeps the research workflow separate from the search-provider implementation.

## Tests

    python -m unittest discover -s tests -v

Offline tests cover deterministic query planning, empty input handling, report source links, and structural review checks. They do not require an API key and do not test live provider availability.

## Limitations

- Search quality and availability depend on DuckDuckGo and network access.
- LLM quality depends on the configured provider/model and retrieved snippets.
- The system does not guarantee source authority or factual correctness; users must inspect linked sources.
- The reviewer provides a critique, not a verified fact-check.
- This is a learning/demo project, not a production research system.

## License

Original project code is provided under the MIT License. Upstream OWL is a separate project under Apache 2.0; see UPSTREAM.md.
