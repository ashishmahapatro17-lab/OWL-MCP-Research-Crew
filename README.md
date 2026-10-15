# OWL-MCP Research Crew

A focused, educational research workflow inspired by the multi-agent and tool-using ideas in [CAMEL-AI OWL](https://github.com/camel-ai/owl). It demonstrates a **Planner → Researcher → Writer → Reviewer** pipeline, with web search exposed as a real tool through the **Model Context Protocol (MCP)**.

> **Scope and attribution:** This is a small independent learning project, not the official OWL framework and not a copy of the full OWL repository. CAMEL-AI OWL is the upstream inspiration; see [UPSTREAM.md](UPSTREAM.md).

## What it does

1. **Planner** turns a research question into a small set of search queries.
2. **Researcher** calls a local MCP server that runs DuckDuckGo searches and returns titled results with source URLs.
3. **Writer** creates a readable report from the retrieved evidence.
4. **Reviewer** checks that the report has evidence and flags when the search returned too little information.
5. **Source list** preserves result titles and URLs so a reader can inspect the original pages.

This is a transparent, rule-based orchestration demo: it does not claim to train models or guarantee that every source is authoritative. Search results can be incomplete or inaccurate; verify important claims against the linked pages.

## Architecture

```text
Research question
       |
    Planner
       | search queries
    Researcher
       | MCP Client (stdio)
       v
  MCP Search Server ----> DuckDuckGo search
       |
  Search results + URLs
       |
     Writer
       |
    Reviewer
       |
  Markdown report
```

## Requirements

- Python 3.10 or newer
- Internet access for DuckDuckGo searches

## Quick start

### macOS / Linux

```bash
git clone https://github.com/ashishmahapatro17-lab/OWL-MCP-Research-Crew.git
cd OWL-MCP-Research-Crew

python3 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
pip install -r requirements.txt

python main.py "How is MCP used to connect AI applications to tools?"
```

### Windows PowerShell

```powershell
git clone https://github.com/ashishmahapatro17-lab/OWL-MCP-Research-Crew.git
cd OWL-MCP-Research-Crew

py -m venv .venv
.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
pip install -r requirements.txt

python main.py "How is MCP used to connect AI applications to tools?"
```

The report is printed in the terminal and saved under `reports/`.

## Example command

```bash
python main.py "Benefits and limitations of retrieval-augmented generation"
```

## Project structure

```text
.
├── main.py                 # Coordinates the research workflow
├── research_crew/
│   ├── __init__.py
│   ├── agents.py           # Planner, Writer, Reviewer stages
│   ├── mcp_client.py       # Starts MCP server and invokes its tool
│   └── report.py           # Markdown report and source list
├── mcp_server/
│   └── search_server.py    # MCP tool backed by DuckDuckGo search
├── reports/                # Generated reports (ignored by Git)
├── requirements.txt
├── .env.example
└── UPSTREAM.md             # Attribution and project boundaries
```

## How MCP is used

The search server exposes a `search_web` tool. The client launches that server as a subprocess over standard input/output (stdio), discovers the available tool, and calls it through an MCP session. This separates the research workflow from the implementation of the search tool.

## Current limitations

- Search quality and availability depend on DuckDuckGo and network access.
- The Planner, Writer, and Reviewer are deliberately simple Python stages, not separate LLM-powered autonomous agents.
- The Reviewer performs basic completeness checks; it does not fact-check every claim.
- This is a learning/demo project, not a production research system.

## Next improvements

- Add an optional LLM-backed synthesis stage with explicit model configuration.
- Add unit tests and saved example outputs.
- Add stronger claim-to-source verification and retry policies.

## License

The original project code in this repository is provided under the MIT License; see [LICENSE](LICENSE). Upstream OWL is a separate project licensed under Apache 2.0. See [UPSTREAM.md](UPSTREAM.md) for attribution.
