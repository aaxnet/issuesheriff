<div align="center">

```
 ██╗███████╗███████╗██╗   ██╗███████╗███████╗██╗  ██╗███████╗██████╗ ██╗███████╗███████╗
 ██║██╔════╝██╔════╝██║   ██║██╔════╝██╔════╝██║  ██║██╔════╝██╔══██╗██║██╔════╝██╔════╝
 ██║███████╗███████╗██║   ██║█████╗  ███████╗███████║█████╗  ██████╔╝██║█████╗  █████╗  
 ██║╚════██║╚════██║██║   ██║██╔══╝  ╚════██║██╔══██║██╔══╝  ██╔══██╗██║██╔══╝  ██╔══╝  
 ██║███████║███████║╚██████╔╝███████╗███████║██║  ██║███████╗██║  ██║██║██║     ██║     
 ╚═╝╚══════╝╚══════╝ ╚═════╝ ╚══════╝╚══════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝╚═╝     ╚═╝   
```

**AI-триаж GitHub issues — прямо в терминале, за секунды.**

<br/>

[![PyPI](https://img.shields.io/pypi/v/issuesheriff?style=flat-square&color=black)](https://pypi.org/project/issuesheriff/)
[![Python](https://img.shields.io/badge/python-3.10+-black?style=flat-square)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-black?style=flat-square)](LICENSE)
[![CI](https://img.shields.io/github/actions/workflow/status/aaxnet/issuesheriff/tests.yml?style=flat-square&color=black)](https://github.com/aaxnet/issuesheriff/actions)
[![Downloads](https://img.shields.io/pypi/dm/issuesheriff?style=flat-square&color=black)](https://pypi.org/project/issuesheriff/)

<br/>

<img src="demo.gif" alt="IssueSheriff demo" width="740"/>

<br/><br/>

</div>

---

## Проблема

Ты открываешь репозиторий после выходных. **47 новых issues.**  
Дубликаты, расплывчатые баг-репорты, фичи под видом багов, вопросы, которым место в Discussions.  
Уходит час только на чтение и разметку.

**IssueSheriff решает это.**

Одна команда:
- сканирует весь issue-трекер
- классифицирует каждую заявку
- находит дубликаты
- предлагает labels
- готовит ответы, которые можно сразу отправлять

И всё это — за время, пока закипает кофе.

---

## Установка

```bash
pip install issuesheriff
```

> Работает из коробки без API-ключа. AI-функции включаются автоматически, если задан `OPENAI_API_KEY`.

---

## Быстрый старт за 30 секунд

```bash
# 1. Укажи токены
export GITHUB_TOKEN=ghp_...
export OPENAI_API_KEY=sk-...      # необязательно — включает AI-ответы и более умную классификацию

# 2. Просканируй любой репозиторий
issuesheriff scan aaxnet/issuesheriff

# 3. Предложи и применяй labels для конкретного issue
issuesheriff labels aaxnet/issuesheriff 42 --apply

# 4. Сгенерируй ответ от мейнтейнера и скопируй его в буфер обмена
issuesheriff reply aaxnet/issuesheriff 42 --copy
```

Вот и всё.

---

## Что умеет

| Команда | Что происходит |
|---|---|
| `scan <owner/repo>` | Читает все открытые issues, классифицирует их, отмечает дубликаты и выводит понятную сводку |
| `analyze <file.json>` | Глубоко анализирует один issue: тип, labels, уровень уверенности, похожие issues, черновик ответа |
| `labels <owner/repo> <#>` | Предлагает labels для одного issue; `--apply` записывает их в GitHub |
| `reply <owner/repo> <#>` | Генерирует живой ответ от мейнтейнера; `--copy` кладёт его в буфер обмена |

---

## Полезный вывод

Запусти `issuesheriff scan microsoft/vscode --limit 50` и получишь:

```text
┌─────────────────────────────────────────────────────────────────┐
│  Просканировано 50 issues · microsoft/vscode · 3.2s            │
├──────┬──────────────────────────────────────┬────────┬──────────┤
│  #   │  Заголовок                           │ Тип    │ Labels   │
├──────┼──────────────────────────────────────┼────────┼──────────┤
│  209 │ Extension host crashes on startup   │ bug    │ bug,crash│
│  208 │ Add vim keybindings to terminal     │ feat   │ feature  │
│  207 │ How do I change the default shell?   │ docs   │ question │
│  206 │ [DUP] Terminal not opening  ──→ #201│ dup    │ duplicate│
└──────┴──────────────────────────────────────┴────────┴──────────┘

  Bugs: 21   Features: 14   Questions: 9   Duplicates: 6
```

А `issuesheriff analyze issue.json` возвращает структурированный JSON, который можно передавать куда угодно:

```json
{
  "summary": "Приложение аварийно закрывается сразу после запуска после последнего обновления.",
  "type": "bug",
  "labels": ["bug", "crash", "regression"],
  "confidence": 0.94,
  "similar_issues": [
    { "id": 209831, "score": 0.81 },
    { "id": 208104, "score": 0.57 }
  ],
  "reply": "Спасибо за репорт — похоже, это регрессия, связанная с недавним крашем. Мы проверим это и сообщим обновления здесь."
}
```

---

## Автоматизация через GitHub Actions

Добавь это в `.github/workflows/triage.yml`, и каждый новый issue будет обрабатываться автоматически:

```yaml
name: Auto Triage

on:
  issues:
    types: [opened, reopened]

permissions:
  issues: write
  contents: read

jobs:
  triage:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install IssueSheriff
        run: pip install issuesheriff

      - name: Analyze & label
        run: |
          echo '{"title":"${{ github.event.issue.title }}","body":"${{ github.event.issue.body }}"}' > issue.json
          issuesheriff analyze issue.json --json > result.json
          cat result.json
        env:
          GITHUB_TOKEN:    ${{ secrets.GITHUB_TOKEN }}
          OPENAI_API_KEY:  ${{ secrets.OPENAI_API_KEY }}
```

---

## AI-бэкенды

IssueSheriff работает с тремя бэкендами — выбирай тот, который подходит под твой стек.

### OpenAI (по умолчанию)
Лучшая точность, самая простая настройка:

```env
OPENAI_API_KEY=sk-...
ISSUESHERIFF_MODEL=gpt-4o-mini   # недорого и быстро; при необходимости замени на gpt-4o
```

### Ollama — полностью офлайн
Никакие данные не покидают твою машину:

```bash
ollama run mistral
```

```env
OLLAMA_MODEL=mistral
OLLAMA_BASE_URL=http://localhost:11434
```

### Без AI
Если ключ не указан, IssueSheriff всё равно работает — эвристическая классификация и поиск дубликатов через TF-IDF доступны без API:

```bash
issuesheriff scan aaxnet/issuesheriff --no-reply
```

---

## Конфигурация

| Переменная | Значение по умолчанию | Описание |
|---|---|---|
| `GITHUB_TOKEN` | — | GitHub token с правом `issues: write` |
| `OPENAI_API_KEY` | — | OpenAI key (необязательно) |
| `ISSUESHERIFF_MODEL` | `gpt-4o-mini` | Модель OpenAI |
| `OLLAMA_MODEL` | — | Имя локальной модели Ollama |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Сервер Ollama |
| `SIMILARITY_THRESHOLD` | `0.45` | Порог cosine similarity для дубликатов |
| `MAX_ISSUES` | `100` | Максимум issues, которые забираются за один scan |

---

## Варианты установки

```bash
# Только основа
pip install issuesheriff

# + поиск дубликатов (TF-IDF cosine similarity)
pip install "issuesheriff[similarity]"

# + поддержка Ollama
pip install "issuesheriff[similarity,ollama]"

# Полная dev-сборка
pip install "issuesheriff[similarity,ollama,dev]"
```

---

## Структура проекта

```text
issuesheriff/
├── issuesheriff/
│   ├── main.py          # CLI entry point
│   ├── ai.py            # AI backends (OpenAI / Ollama / heuristic)
│   ├── github_client.py # GitHub API wrapper
│   ├── similarity.py    # TF-IDF duplicate detection
│   ├── config.py        # Env + settings
│   └── utils.py
├── tests/
├── examples/
│   └── sample_issue.json
├── .github/
│   └── workflows/
├── .env.example
└── pyproject.toml
```

---

## Локальная разработка

```bash
git clone https://github.com/aaxnet/issuesheriff
cd issuesheriff
pip install -e ".[dev,similarity]"
pytest
ruff check .
```

PR приветствуются. Загляни в [open issues](https://github.com/aaxnet/issuesheriff/issues) — там часто есть хорошие задачи для старта.

---

<div align="center">

**Если IssueSheriff сэкономил тебе время, ⭐ поможет другим найти проект.**

[PyPI](https://pypi.org/project/issuesheriff/) · [Сообщить о баге](https://github.com/aaxnet/issuesheriff/issues/new) · [Предложить фичу](https://github.com/aaxnet/issuesheriff/issues/new)

</div>
