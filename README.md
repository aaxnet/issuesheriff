<div align="center">

```text
 ██╗███████╗███████╗██╗   ██╗███████╗███████╗██╗  ██╗███████╗██████╗ ██╗███████╗███████╗
 ██║██╔════╝██╔════╝██║   ██║██╔════╝██╔════╝██║  ██║██╔════╝██╔══██╗██║██╔════╝██╔════╝
 ██║███████╗███████╗██║   ██║█████╗  ███████╗███████║█████╗  ██████╔╝██║█████╗  █████╗  
 ██║╚════██║╚════██║██║   ██║██╔══╝  ╚════██║██╔══██║██╔══╝  ██╔══██╗██║██╔══╝  ██╔══╝  
 ██║███████║███████║╚██████╔╝███████╗███████║██║  ██║███████╗██║  ██║██║██║     ██║     
 ╚═╝╚══════╝╚══════╝ ╚═════╝ ╚══════╝╚══════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝╚═╝     ╚═╝     
```

# IssueSheriff

### AI-powered GitHub issue intelligence for maintainers who value speed, clarity, and polish.

<br/>

[![PyPI](https://img.shields.io/pypi/v/issuesheriff?style=flat-square\&color=black)](https://pypi.org/project/issuesheriff/)
[![Python](https://img.shields.io/badge/python-3.10+-black?style=flat-square)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-black?style=flat-square)](LICENSE)
[![CI](https://img.shields.io/github/actions/workflow/status/aaxnet/issuesheriff/tests.yml?style=flat-square\&color=black)](https://github.com/aaxnet/issuesheriff/actions)
[![Downloads](https://img.shields.io/pypi/dm/issuesheriff?style=flat-square\&color=black)](https://pypi.org/project/issuesheriff/)

<br/>

</div>

> **IssueSheriff** turns noisy GitHub issue trackers into clean, structured workflows.
> It classifies issues, suggests labels, detects duplicates, and drafts replies — from your terminal or inside GitHub Actions.

---

## Why it exists

Large repositories accumulate issues fast. Manual triage is repetitive, slow, and easy to get wrong.

IssueSheriff helps you:

* identify issue type quickly
* suggest relevant labels
* detect likely duplicates
* generate concise maintainer replies
* automate triage in CI/CD

---

## Highlights

| Capability        | What it does                                                   |
| ----------------- | -------------------------------------------------------------- |
| 🔍 Analyze        | Classifies issues as bug, feature, question, docs, or security |
| 🏷 Labels         | Suggests relevant labels and can apply them automatically      |
| 🪞 Duplicates     | Finds similar issues using TF-IDF + cosine similarity          |
| 💬 Replies        | Drafts human-sounding maintainer responses                     |
| 📡 Scan           | Reads whole repositories with pagination support               |
| ⚡ GitHub Action   | Auto-triage on new issues                                      |
| 🦙 Offline mode   | Works with Ollama locally                                      |
| 🔌 No-AI fallback | Still useful without an API key                                |

---

## Install

```bash
pip install issuesheriff
```

With duplicate detection:

```bash
pip install "issuesheriff[similarity]"
```

Full dev setup:

```bash
pip install "issuesheriff[similarity,ollama,dev]"
```

---

## Quick start

```bash
cp .env.example .env
```

```env
GITHUB_TOKEN=ghp_your_token_here
OPENAI_API_KEY=sk_your_key_here
```

```bash
issuesheriff analyze examples/sample_issue.json
issuesheriff scan aaxnet/issuesheriff --limit 25
issuesheriff labels aaxnet/issuesheriff 123 --apply
issuesheriff reply aaxnet/issuesheriff 123 --copy
```

---

## CLI

```bash
issuesheriff analyze <file>          Analyze a local issue JSON file
issuesheriff scan <owner/repo>       Scan a GitHub repository
issuesheriff labels <owner/repo> <#> Suggest or apply labels
issuesheriff reply <owner/repo> <#>  Generate a reply draft
```

Examples:

```bash
issuesheriff scan microsoft/vscode --limit 50 --state open
issuesheriff scan torvalds/linux --limit 100 --no-duplicates
issuesheriff analyze issue.json --json
issuesheriff reply aaxnet/issuesheriff 42 --copy
```

---

## GitHub Action

```yaml
name: IssueSheriff Auto Triage

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

      - name: Analyze issue
        run: |
          echo '{"title":"${{ github.event.issue.title }}","body":"${{ github.event.issue.body }}"}' > issue.json
          issuesheriff analyze issue.json --json > result.json
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

---

## Data format

### Input

```json
{
  "title": "App crashes on startup",
  "body": "The app exits immediately after launch.",
  "comments": []
}
```

### Output

```json
{
  "summary": "Application crashes immediately on launch and appears reproducible after the latest update.",
  "type": "bug",
  "labels": ["bug", "crash"],
  "confidence": 0.94,
  "similar_issues": [
    { "id": 209831, "score": 0.81 },
    { "id": 208104, "score": 0.57 }
  ],
  "reply": "Thanks for the report. This looks like a crash regression, and we will investigate it further."
}
```

---

## AI backends

### OpenAI

Fast and accurate for production use.

```env
OPENAI_API_KEY=sk-...
ISSUESHERIFF_MODEL=gpt-4o-mini
```

### Ollama

Private local inference with no data leaving your machine.

```bash
ollama run mistral
```

```env
OLLAMA_MODEL=mistral
OLLAMA_BASE_URL=http://localhost:11434
```

### No AI

If no backend is configured, IssueSheriff still runs with heuristic classification and duplicate detection.

```bash
issuesheriff scan aaxnet/issuesheriff --no-reply
```

---

## Configuration

| Variable               |                  Default | Description                     |
| ---------------------- | -----------------------: | ------------------------------- |
| `GITHUB_TOKEN`         |                        — | GitHub token with issues access |
| `OPENAI_API_KEY`       |                        — | OpenAI API key                  |
| `ISSUESHERIFF_MODEL`   |            `gpt-4o-mini` | OpenAI model                    |
| `OLLAMA_MODEL`         |                        — | Local Ollama model              |
| `OLLAMA_BASE_URL`      | `http://localhost:11434` | Ollama server URL               |
| `SIMILARITY_THRESHOLD` |                   `0.45` | Duplicate match threshold       |
| `MAX_ISSUES`           |                    `100` | Maximum issues per scan         |

---

## Development

```bash
git clone https://github.com/aaxnet/issuesheriff
cd issuesheriff
pip install -e ".[dev,similarity]"
pytest
ruff check .
```

---

## Project structure

```text
issuesheriff/
├── issuesheriff/
│   ├── main.py
│   ├── ai.py
│   ├── github_client.py
│   ├── similarity.py
│   ├── config.py
│   └── utils.py
├── tests/
├── examples/
├── .github/workflows/
├── .env.example
└── pyproject.toml
```

---

## Roadmap

* GitHub App integration
* semantic embeddings backend
* stale issue detection
* web dashboard
* Slack / Discord
