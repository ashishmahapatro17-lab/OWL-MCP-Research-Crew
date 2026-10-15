# Upstream attribution and scope

This repository is an independent educational demo inspired by the multi-agent, tool-using workflow and MCP integration concepts in **CAMEL-AI OWL**.

- Upstream project: https://github.com/camel-ai/owl
- Upstream license: Apache License 2.0
- Upstream paper: https://arxiv.org/abs/2505.23885

The current repository does **not** vendor or copy the OWL codebase. Its Python workflow stages and MCP search server are a small, separately written demonstration intended to make the orchestration and tool boundary easy to study.

The upstream project's README identifies its source code as Apache 2.0 licensed. If upstream source files are incorporated in a future version, preserve the applicable copyright and license notices and identify those changes clearly. See the upstream repository for the authoritative license and notices.

## What is implemented here

- A deterministic query-planning stage
- A real MCP stdio client/server interaction
- DuckDuckGo-backed search results with source URLs
- Markdown report generation
- Basic structural review checks

## What is not claimed

- This is not the official OWL framework.
- The workflow stages are not separate autonomous LLM agents.
- The reviewer does not prove factual correctness.
- No benchmark results or accuracy claims are made.
