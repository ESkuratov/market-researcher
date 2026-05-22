# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI Market Researcher Agent — single-agent system built with LangGraph that collects company data from external APIs and generates structured analytical reports in Russian.

## Stack

- **Language**: Python 3.x
- **AI Framework**: LangGraph (prebuilt `create_react_agent`) + LangChain (tool decorators)
- **AI Model**: Ollama (local or cloud models), configured via `.env`
- **Key Libraries**: `yfinance`, `tavily-python`, `feedparser`, `python-dotenv`, `langgraph-prebuilt`, `langchain-ollama`

## Architecture

- `main.py` — entry point: reads query from CLI args or stdin, calls `run_agent()`
- `agent.py` — builds a LangGraph ReAct agent with `ChatOllama` LLM and two tools
- `tools.py` — two `@tool`-decorated functions:

### Tools

1. `get_company_profile(company_name)` — yfinance (primary, requires ticker), Wikipedia REST API (fallback, accepts full names)
2. `get_financial_news(company_name)` — Tavily Search API (primary), Google News RSS (fallback)

### Agent Behavior

- Input: natural language query like "Составь аналитический отчет по компании Apple"
- The LLM decides tool call order and synthesis — the system prompt instructs it to call profile first, then news, then generate report
- Console logging at each step (`[INFO] Думаю...`, `[TOOL] Вызываю get_company_profile для Apple...`)
- Edge cases: unknown companies → agent detects invalid data and reports insufficient info

### Output Format

Markdown report:
- Company name, sector, country, market cap
- News summary with positive/negative factors
- Conclusion with short-term outlook

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

`.env` file:
```
TAVILY_API_KEY=tvly-...
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=deepseek-v3.2:cloud
```

## Known Behaviors

- yfinance requires stock tickers (AAPL, TSLA), not full names. For full names Wikipedia fallback activates.
- Wikipedia search can return irrelevant results for obscure queries — agent-level validation catches this.
- Tavily uses the API key from `.env`; without it, Google News RSS is used.
