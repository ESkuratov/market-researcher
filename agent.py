import os

from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent

from prompts import SYSTEM_PROMPT
from tools import get_company_profile, get_financial_news


def _normalize_base_url(url: str) -> str:
    """Strip trailing /api and slashes — ollama client appends /api/... itself."""
    return url.rstrip("/").removesuffix("/api").rstrip("/")


def run_agent(query: str) -> str:
    api_key = os.getenv("OLLAMA_API_KEY")
    model_name = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    base_url = _normalize_base_url(base_url)

    kwargs = dict(
        model=model_name,
        base_url=base_url,
        temperature=0.7,
    )
    if api_key:
        kwargs["client_kwargs"] = {
            "headers": {"Authorization": f"Bearer {api_key}"}
        }

    llm = ChatOllama(**kwargs)

    tools = [get_company_profile, get_financial_news]

    agent = create_react_agent(
        model=llm,
        tools=tools,
        prompt=SYSTEM_PROMPT,
    )

    print("[INFO] Думаю...")

    final_content = ""
    for chunk in agent.stream({"messages": [("human", query)]}):
        for node_name, values in chunk.items():
            if "messages" in values:
                msg = values["messages"][-1]
                # Если это текстовый ответ агента — сохраняем
                if hasattr(msg, "content") and isinstance(msg.content, str) and msg.content:
                    final_content = msg.content

    print("[INFO] Формирую отчёт...")
    return final_content
