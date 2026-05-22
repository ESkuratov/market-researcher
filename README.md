# AI Market Researcher Agent

Agent для сбора данных о компании из внешних API и формирования структурированного аналитического отчёта в Markdown.

## Стек

- **AI-агент:** LangGraph (`create_react_agent`) — ReAct-цикл из коробки
- **LLM:** Ollama Cloud (модель `kimi-k2.6:cloud` с поддержкой tool calling)
- **Профиль компании:** yfinance (основной) → Wikipedia REST API (запасной)
- **Новости:** Tavily Search API (основной) → Google News RSS (запасной)

## Требования

- Python 3.10+
- [Ollama](https://ollama.com/) аккаунт для доступа к облачным моделям

## Установка

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Настройка

Скопируйте `.env.example` в `.env`:

```bash
cp .env.example .env
```

Переменные окружения:

| Переменная | Обязательная | Описание |
|------------|-------------|----------|
| `OLLAMA_BASE_URL` | да | URL сервера Ollama (`https://ollama.com/api`) |
| `OLLAMA_MODEL` | да | Модель (`kimi-k2.6:cloud`) |
| `OLLAMA_API_KEY` | да | Ключ для Ollama Cloud |
| `TAVILY_API_KEY` | нет | Ключ с [tavily.com](https://tavily.com) (иначе RSS) |

## Запуск

```bash
python main.py "Составь аналитический отчет по компании Apple"
```

Или через stdin:

```bash
echo "Составь аналитический отчет по компании Tesla" | python main.py
```

## Пример вывода

```
[INFO] Думаю...
[TOOL] Вызываю get_company_profile для Apple...
[TOOL] Вызываю get_financial_news для Apple...
[TOOL] Tavily error: превышен лимит, switching to RSS fallback
[TOOL] Получил ответ от get_financial_news (RSS)
[TOOL] Получил ответ от get_company_profile (Wikipedia: Apple Inc.)
[INFO] Формирую отчёт...

## Аналитический отчёт: Apple Inc.

**Сфера деятельности:** Потребительская электроника, ПО, онлайн-сервисы
**Страна:** США
**Капитализация:** Данные не предоставлены

### Анализ новостей
**Позитивные факторы:** ...
**Негативные факторы:** ...

### Заключение
Краткосрочные перспективы: ...
```

## Архитектура

```
main.py → agent.py (ReAct loop) → tools.py (2 инструмента)
                                      ├── get_company_profile
                                      │   ├── yfinance (primary)
                                      │   └── Wikipedia search → summary (fallback)
                                      └── get_financial_news
                                          ├── Tavily API (primary)
                                          └── Google News RSS (fallback)

prompts.py → SYSTEM_PROMPT (импортируется в agent.py)
```

LangGraph управляет ReAct-циклом: LLM решает, какой инструмент вызвать и когда, получает результат (Observation) и формирует финальный ответ.

### Структура файлов

| Файл | Назначение |
|------|-----------|
| `main.py` | Точка входа, загрузка `.env`, вызов агента |
| `agent.py` | ReAct-агент LangGraph, инициализация LLM |
| `prompts.py` | Системный промпт с инструкциями и правилами |
| `tools.py` | Инструменты: get_company_profile, get_financial_news |

## Обработка ошибок

- **Неизвестная компания:** Инструмент возвращает ошибку, агент сообщает, что данных недостаточно
- **yfinance не находит имя:** Fallback на Wikipedia (с поиском через Search API)
- **Tavily недоступен:** Fallback на Google News RSS
- **Вопрос не по теме:** Агент отвечает заглушкой — «Я — аналитический AI-агент...»
- **Ollama Cloud:** API-ключ передаётся через `Authorization: Bearer` в `client_kwargs`

## BRD

Бизнес-требования проекта описаны в [`brd.md`](brd.md).

## Смена LLM-провайдера

В `agent.py` достаточно заменить `ChatOllama` на другую модель LangChain:

```python
# Anthropic
from langchain_anthropic import ChatAnthropic
llm = ChatAnthropic(model="claude-sonnet-4-6")

# OpenAI
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model="gpt-4o")
```
