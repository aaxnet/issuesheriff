<div align="center">

```
 ██╗███████╗███████╗██╗   ██╗███████╗███████╗██╗  ██╗███████╗██████╗ ██╗███████╗███████╗
 ██║██╔════╝██╔════╝██║   ██║██╔════╝██╔════╝██║  ██║██╔════╝██╔══██╗██║██╔════╝██╔════╝
 ██║███████╗███████╗██║   ██║█████╗  ███████╗███████║█████╗  ██████╔╝██║█████╗  █████╗  
 ██║╚════██║╚════██║██║   ██║██╔══╝  ╚════██║██╔══██║██╔══╝  ██╔══██╗██║██╔══╝  ██╔══╝  
 ██║███████║███████║╚██████╔╝███████╗███████║██║  ██║███████╗██║  ██║██║██║     ██║     
 ╚═╝╚══════╝╚══════╝ ╚═════╝ ╚══════╝╚══════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝╚═╝     ╚═╝     
```

# IssueSheriff

### AI-powered GitHub Issue Intelligence Engine

Turn messy issue trackers into clean, structured, production-ready workflows.

<br/>

[![PyPI](https://img.shields.io/pypi/v/issuesheriff?color=black\&style=flat-square)](https://pypi.org/project/issuesheriff/)
[![Python](https://img.shields.io/badge/python-3.10+-black?style=flat-square)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-black?style=flat-square)](LICENSE)
[![CI](https://img.shields.io/github/actions/workflow/status/aaxnet/issuesheriff/tests.yml?style=flat-square\&color=black)](https://github.com/aaxnet/issuesheriff/actions)
[![Downloads](https://img.shields.io/pypi/dm/issuesheriff?color=black\&style=flat-square)](https://pypi.org/project/issuesheriff/)

<br/>

</div>

---

## ⚡ Overview

**IssueSheriff** is a high-performance AI system for GitHub issue triage.

It automatically:

* classifies issues (bug / feature / security / docs)
* suggests labels
* detects duplicates using semantic similarity
* generates maintainer-quality replies
* processes entire repositories via CLI or CI/CD

No noise. No manual triage overload.

---

## 🚀 Install

```bash
pip install issuesheriff
```

With full capabilities:

```bash
pip install "issuesheriff[similarity,ollama,dev]"
```

---

## ⚡ Quick Start

```bash
cp .env.example .env
```

```env
GITHUB_TOKEN=ghp_xxx
OPENAI_API_KEY=sk-xxx
```

```bash
issuesheriff scan aaxnet/issuesheriff --limit 20
```

---

## 🧠 Core Features

| Feature       | Description                                         |
| ------------- | --------------------------------------------------- |
| 🔍 Analyze    | Classify issue type with AI/heuristics              |
| 🏷 Labels     | Auto-suggest and apply labels                       |
| 🪞 Duplicates | Semantic similarity detection (TF-IDF / embeddings) |
| 💬 Replies    | Generate human-quality maintainer responses         |
| 📡 Scan       | Bulk repo processing via GitHub API                 |
| ⚙ CI/CD       | GitHub Actions integration                          |
| 🦙 Offline    | Ollama local model support                          |
| 🧩 Fallback   | Works without any AI API                            |

---

## 📦 CLI Usage

```bash
issuesheriff analyze issue.json
issuesheriff scan owner/repo --limit 50
issuesheriff labels owner/repo 123 --apply
issuesheriff reply owner/repo 123 --copy
```

---

## 🔥 GitHub Action

```yaml
name: IssueSheriff Auto Triage

on:
  issues:
    types: [opened]

permissions:
  issues: write

jobs:
  triage:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install
        run: pip install issuesheriff

      - name: Run Triage
        run: |
          echo '{"title":"${{ github.event.issue.title }}","body":"${{ github.event.issue.body }}"}' > issue.json
          issuesheriff analyze issue.json
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

---

## 🧬 Architecture

```
issuesheriff/
├── ai.py            # LLM + fallback logic
├── github_client.py # GitHub API layer
├── similarity.py    # duplicate detection engine
├── main.py          # CLI (Typer)
├── config.py        # env config
└── utils.py
```

---

## ⚙ Configuration

| Variable             | Description           |
| -------------------- | --------------------- |
| GITHUB_TOKEN         | GitHub API access     |
| OPENAI_API_KEY       | AI backend            |
| ISSUESHERIFF_MODEL   | Model selection       |
| SIMILARITY_THRESHOLD | Duplicate sensitivity |

---

## 🧪 Development

```bash
pip install -e ".[dev,similarity]"
pytest
ruff check .
```

---

## 🧭 Roadmap

* GitHub App integration
* Web dashboard
* Slack / Discord notifications
* Advanced embeddings (sentence-transformers)
* Auto-stale issue management

---

## 📜 License

MIT License © aaxnet

---

<div align="center">

### Built for developers who value time over triage.

[GitHub]([https://github.com](https://github.com)
