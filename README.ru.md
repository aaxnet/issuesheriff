<div align="center">

```
██╗███████╗███████╗██╗   ██╗███████╗███████╗██╗  ██╗███████╗██████╗ ██╗███████╗███████╗
██║██╔════╝██╔════╝██║   ██║██╔════╝██╔════╝██║  ██║██╔════╝██╔══██╗██║██╔════╝██╔════╝
██║███████╗███████╗██║   ██║█████╗  ███████╗███████║█████╗  ██████╔╝██║█████╗  █████╗
██║╚════██║╚════██║██║   ██║██╔══╝  ╚════██║██╔══██║██╔══╝  ██╔══██╗██║██╔══╝  ██╔══╝
██║███████║███████║╚██████╔╝███████╗███████║██║  ██║███████╗██║  ██║██║██║     ██║
╚═╝╚══════╝╚══════╝ ╚═════╝ ╚══════╝╚══════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝╚═╝     ╚═╝
```

### AI-триаж GitHub Issues — прямо в терминале, за секунды.

<br/>

[![PyPI](https://img.shields.io/pypi/v/issuesheriff?style=flat-square&color=black)](https://pypi.org/project/issuesheriff/)
[![Python](https://img.shields.io/badge/python-3.10+-black?style=flat-square)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-black?style=flat-square)](LICENSE)
[![CI](https://img.shields.io/github/actions/workflow/status/aaxnet/issuesheriff/tests.yml?style=flat-square&color=black)](https://github.com/aaxnet/issuesheriff/actions)
[![Downloads](https://img.shields.io/pypi/dm/issuesheriff?style=flat-square&color=black)](https://pypi.org/project/issuesheriff/)

<br/>

<img src="demo.gif" alt="IssueSheriff demo" width="740"/>

<br/>

[![EN](https://img.shields.io/badge/lang-EN-black?style=flat-square)](README.md)
[![PyPI](https://img.shields.io/badge/PyPI-пакет-black?style=flat-square&logo=pypi&logoColor=white)](https://pypi.org/project/issuesheriff/)
[![Bug](https://img.shields.io/badge/сообщить-баг-black?style=flat-square&logo=github&logoColor=white)](https://github.com/aaxnet/issuesheriff/issues/new)
[![Feature](https://img.shields.io/badge/предложить-фичу-black?style=flat-square&logo=github&logoColor=white)](https://github.com/aaxnet/issuesheriff/issues/new)

</div>

---

## Проблема

Ты открываешь репо после выходных. **47 новых issues.**

Дубликаты. Размытые баг-репорты. Feature request, замаскированный под баг. Вопросы, которым место в Discussions. Ты тратишь час только на чтение и расстановку лейблов — ещё до того, как написал хоть строчку кода.

**IssueSheriff решает это.**

Одна команда сканирует весь трекер, классифицирует каждый issue, находит дубликаты, предлагает лейблы и генерирует готовые ответы мейнтейнера — пока варится кофе.

---

## Установка

```bash
pip install issuesheriff

# Рекомендуется — включает определение дублей
pip install "issuesheriff[similarity]"
```

> Работает из коробки **без API-ключа.** AI-функции активируются автоматически при настройке.

---

## Быстрый старт

### <img src="assets/icons/gear.svg" width="15" height="15"> Шаг 1 — Настройка (один раз)

```bash
issuesheriff setup
```

Интерактивный визард спрашивает GitHub-токен и при желании AI-бэкенд. Всё сохраняется в `~/.config/issuesheriff/.env` — больше никаких `export` перед каждым запуском.

```
┌─────────────────────────────────────────────────┐
│  IssueSheriff Setup Wizard                      │
│  Enter = оставить текущее значение в скобках.   │
└─────────────────────────────────────────────────┘

── Обязательно ───────────────────────────────────
  GitHub Token (repo + issues:write): ghp_***
── AI-бэкенд (оба опциональны) ──────────────────
  OpenAI API Key (пропустить — Enter): sk-***
  Ollama model  (пропустить — Enter):
── Тонкая настройка (опционально) ───────────────
  Порог дублей (по умолчанию 0.45):
  Макс. issues за скан (по умолчанию 100):

✓ Сохранено: ~/.config/issuesheriff/.env
```

> **Где взять GitHub-токен** → [github.com/settings/tokens](https://github.com/settings/tokens) → Generate new token (classic) → отметь `repo` + `write:issues`

### <img src="assets/icons/radar.svg" width="15" height="15"> Шаг 2 — Запуск

```bash
# Сканировать репозиторий
issuesheriff scan microsoft/vscode --limit 20

# Поставить лейблы на конкретный issue
issuesheriff labels microsoft/vscode 42 --apply

# Сгенерировать ответ мейнтейнера (скопировать в буфер)
issuesheriff reply microsoft/vscode 42 --copy

# Проанализировать issue из локального JSON-файла
issuesheriff analyze issue.json
```

---

## Что умеет

| | Команда | Что делает |
|:---:|---|---|
| <img src="assets/icons/gear.svg" width="14" height="14"> | `setup` | Интерактивная настройка — токены и AI-бэкенд один раз |
| <img src="assets/icons/radar.svg" width="14" height="14"> | `scan <owner/repo>` | Загрузить все открытые issues, классифицировать, найти дубли, вывести сводку |
| <img src="assets/icons/search.svg" width="14" height="14"> | `analyze <file.json>` | Глубокий анализ одного issue — тип, лейблы, уверенность, черновик ответа |
| <img src="assets/icons/tag.svg" width="14" height="14"> | `labels <owner/repo> <#>` | Предложить лейблы для issue; `--apply` запишет их на GitHub |
| <img src="assets/icons/chat.svg" width="14" height="14"> | `reply <owner/repo> <#>` | Сгенерировать живой ответ мейнтейнера; `--copy` положит в буфер обмена |

---

## Как выглядит вывод

```
┌──────────────────────────────────────────────────────────────┐
│  microsoft/vscode  —  20 issues загружено                    │
└──────────────────────────────────────────────────────────────┘

  #209  Extension host crashes on startup  [BUG]
  Краткое: процесс extension host падает сразу при запуске.
  Лейблы  bug  crash

  #208  Add vim keybindings to terminal  [FEATURE]
  Краткое: пользователь просит Vim-режим в терминале.
  Лейблы  feature  terminal

  #207  How do I change the default shell?  [DOCS]
  Краткое: пользователь не знает как настроить шелл по умолчанию.
  Лейблы  question  docs

── Определение дублей ─────────────────────────────────────────

  #206  Terminal not opening  ──→  #201   ████░░ 81%
  #203  Shell crashes on open  ──→  #201  ███░░░ 57%
```

`issuesheriff analyze issue.json --json` возвращает структурированный JSON:

```json
{
  "summary": "Приложение крашится сразу после последнего обновления.",
  "type": "bug",
  "labels": ["bug", "crash", "regression"],
  "confidence": 0.94,
  "similar_issues": [
    { "id": 209831, "score": 0.81 },
    { "id": 208104, "score": 0.57 }
  ],
  "reply": "Спасибо за репорт — похоже на регрессию из последнего обновления. Разберёмся и отпишемся здесь."
}
```

---

## AI-бэкенды

### <img src="assets/icons/cloud.svg" width="14" height="14"> OpenAI — лучшая точность

```bash
issuesheriff setup   # введи sk-... ключ при запросе
```

По умолчанию `gpt-4o-mini` — быстро и дёшево (~$0.001 за issue). Замени на `gpt-4o` для максимальной точности.

### <img src="assets/icons/monitor.svg" width="14" height="14"> Ollama — полностью офлайн

Данные не покидают твою машину:

```bash
ollama pull mistral
issuesheriff setup   # введи "mistral" в поле Ollama model
```

### <img src="assets/icons/bolt.svg" width="14" height="14"> Без AI — нулевая конфигурация

Эвристика + TF-IDF для дублей, без API:

```bash
issuesheriff scan aaxnet/issuesheriff --no-reply
```

---

## <img src="assets/icons/workflow.svg" width="15" height="15"> Автоматизация через GitHub Actions

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
      - run: pip install "issuesheriff[similarity]"
      - run: |
          echo '{"title":"${{ github.event.issue.title }}","body":"${{ github.event.issue.body }}"}' > issue.json
          issuesheriff analyze issue.json --json > result.json
        env:
          GITHUB_TOKEN:   ${{ secrets.GITHUB_TOKEN }}
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

---

## Конфигурация

| Переменная | По умолчанию | Описание |
|---|---|---|
| `GITHUB_TOKEN` | — | GitHub-токен (`repo` + `issues:write`) |
| `OPENAI_API_KEY` | — | OpenAI-ключ — включает AI-классификацию и ответы |
| `ISSUESHERIFF_MODEL` | `gpt-4o-mini` | Модель OpenAI |
| `OLLAMA_MODEL` | — | Локальная Ollama-модель (например `mistral`) |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Адрес Ollama-сервера |
| `SIMILARITY_THRESHOLD` | `0.45` | Порог косинусного сходства для дублей |
| `MAX_ISSUES` | `100` | Макс. issues за один `scan` |

Всё задаётся через `issuesheriff setup` или вручную в `~/.config/issuesheriff/.env`.

---

## Варианты установки

```bash
pip install issuesheriff                          # только ядро
pip install "issuesheriff[similarity]"            # + определение дублей  ← рекомендуется
pip install "issuesheriff[similarity,ollama]"     # + поддержка Ollama
pip install "issuesheriff[similarity,ollama,dev]" # полная установка для разработки
```

---

## Разработка

```bash
git clone https://github.com/aaxnet/issuesheriff
cd issuesheriff
pip install -e ".[dev,similarity]"
pytest && ruff check .
```

PR-ы приветствуются. Смотри [открытые issues](https://github.com/aaxnet/issuesheriff/issues).

---

<div align="center">
<br/>

Если IssueSheriff сэкономил тебе время — <img src="assets/icons/star.svg" width="13" height="13"> помогает другим мейнтейнерам его найти.

<br/>

[![Поставить звезду](https://img.shields.io/badge/Поставить_звезду-black?style=flat-square&logo=github&logoColor=white)](https://github.com/aaxnet/issuesheriff)
[![PyPI](https://img.shields.io/badge/PyPI-black?style=flat-square&logo=pypi&logoColor=white)](https://pypi.org/project/issuesheriff/)
[![Сообщить о баге](https://img.shields.io/badge/Сообщить_о_баге-black?style=flat-square&logo=github&logoColor=white)](https://github.com/aaxnet/issuesheriff/issues/new)

<br/>
</div>
