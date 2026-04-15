<div align="center">

```
 ██╗███████╗███████╗██╗   ██╗███████╗███████╗██╗  ██╗███████╗██████╗ ██╗███████╗███████╗
 ██║██╔════╝██╔════╝██║   ██║██╔════╝██╔════╝██║  ██║██╔════╝██╔══██╗██║██╔════╝██╔════╝
 ██║███████╗███████╗██║   ██║█████╗  ███████╗███████║█████╗  ██████╔╝██║█████╗  █████╗  
 ██║╚════██║╚════██║██║   ██║██╔══╝  ╚════██║██╔══██║██╔══╝  ██╔══██╗██║██╔══╝  ██╔══╝  
 ██║███████║███████║╚██████╔╝███████╗███████║██║  ██║███████╗██║  ██║██║██║     ██║     
 ╚═╝╚══════╝╚══════╝ ╚═════╝ ╚══════╝╚══════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝╚═╝     ╚═╝     
```

### AI-powered GitHub Issue triage — in your terminal.

<br/>

[![PyPI](https://img.shields.io/pypi/v/issuesheriff?color=black&style=flat-square)](https://pypi.org/project/issuesheriff/)
[![Python](https://img.shields.io/badge/python-3.10+-black?style=flat-square)](https://python.org)
[![License: MIT](https://img.shields.io/badge/license-MIT-black?style=flat-square)](LICENSE)
[![Tests](https://img.shields.io/github/actions/workflow/status/yourusername/issuesheriff/tests.yml?style=flat-square&label=tests&color=black)](https://github.com/yourusername/issuesheriff/actions)
[![Downloads](https://img.shields.io/pypi/dm/issuesheriff?color=black&style=flat-square)](https://pypi.org/project/issuesheriff/)

<br/>

</div>

**IssueSheriff** takes your GitHub Issues and runs them through AI — classifying type, suggesting labels, finding duplicates, and drafting replies. One command. Works on any public or private repo.

Use it as a **CLI tool** to triage manually, or drop in the included **GitHub Action** to automate triage on every new issue.

<br/>

```
$ issuesheriff scan microsoft/vscode --limit 10
```

```
  📦 microsoft/vscode  —  10 issues loaded

  ── Issue #210445 ────────────────────────────────────────────────────────────
  Terminal stops rendering after switching tabs                          [BUG]

  Summary
  The integrated terminal goes blank when switching between editor tabs and
  returning to the terminal panel. Reproducible on macOS with GPU acceleration
  enabled since v1.89.

  Labels  bug  performance

  ── Issue #210401 ────────────────────────────────────────────────────────────
  Add support for multiple cursor themes                             [FEATURE]

  Summary
  Users are requesting the ability to customize cursor appearance beyond
  the current three options. Several comments reference VS Code's existing
  cursor style setting as a reference point.

  Labels  feature

  ── Duplicate Detection ──────────────────────────────────────────────────────
  #210445  ↔  #209831  ████████░░  81%  terminal rendering blank on tab switch
  #210201  ↔  #209944  ██████░░░░  63%  cursor theme customization request
```

<br/>

---

## Features

| | |
|:--|:--|
| 🔍 **Analyze** | Classify issues as `bug` / `feature` / `question` / `docs` / `security` |
| 🏷 **Labels** | Suggest relevant labels based on content — apply them with `--apply` |
| 🪞 **Duplicates** | Find similar issues with TF-IDF + cosine similarity (no API key needed) |
| 💬 **Reply** | Generate a maintainer reply draft — human-sounding, under 100 words |
| 📡 **Scan** | Fetch and triage entire repos through the GitHub API with pagination |
| ⚡ **GitHub Action** | Plug-and-play workflow — labels + comment on every new issue automatically |
| 🦙 **Ollama** | Fully offline mode — no API key, no data leaving your machine |
| 🔌 **No AI fallback** | Heuristic classifier + duplicate detection work without any API key |

<br/>

---

## Install

```bash
pip install issuesheriff
```

With duplicate detection (recommended):

```bash
pip install "issuesheriff[similarity]"
```

> Requires Python 3.10+

<br/>

---

## Quickstart

**1. Set up credentials**

```bash
cp .env.example .env
```

```env
GITHUB_TOKEN=ghp_your_token_here
OPENAI_API_KEY=sk-your_key_here
```

**2. Analyze a local issue file**

```bash
issuesheriff analyze examples/sample_issue.json
```

**3. Scan a real repository**

```bash
issuesheriff scan torvalds/linux --limit 25
```

**4. Suggest and apply labels**

```bash
issuesheriff labels microsoft/vscode 210445 --apply
```

**5. Generate a reply draft**

```bash
issuesheriff reply microsoft/vscode 210445 --copy
```

<br/>

---

## CLI Reference

```
issuesheriff analyze <file>          Analyze a local issue JSON file
issuesheriff scan   <owner/repo>     Scan a GitHub repository
issuesheriff labels <owner/repo> <#> Suggest (or apply) labels
issuesheriff reply  <owner/repo> <#> Generate a reply draft
```

### Full options

```bash
# Scan
issuesheriff scan microsoft/vscode --limit 50 --state open
issuesheriff scan torvalds/linux   --limit 100 --no-duplicates
issuesheriff scan myorg/myrepo     --json > report.json

# Labels
issuesheriff labels myorg/myrepo 42 --apply   # writes labels to GitHub

# Reply
issuesheriff reply myorg/myrepo 42 --copy     # copies draft to clipboard

# Analyze
issuesheriff analyze issue.json --json        # machine-readable output
issuesheriff analyze issue.json --no-reply    # skip reply generation
```

<br/>

---

## GitHub Action

Drop automated triage into any repository. IssueSheriff will analyze every new issue — classify it, apply labels, and post a structured summary comment — within seconds of it being opened.

```yaml
# .github/workflows/triage.yml
name: 🔍 IssueSheriff — Auto Triage

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
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}

      # Full workflow with label application and comment posting:
      # see .github/workflows/triage.yml in this repo
```

The full workflow (included in this repo) automatically applies suggested labels and posts a triage comment like this:

> **🔍 IssueSheriff Triage**
>
> **Type:** `bug` | **Labels:** `bug`, `performance`
>
> **Summary:**
> > The integrated terminal goes blank after switching editor tabs on macOS with GPU acceleration enabled since v1.89.
>
> *Automatically triaged by IssueSheriff*

<br/>

---

## Data Formats

**Input — Issue JSON:**

```json
{
  "title": "App crashes on startup with SIGSEGV",
  "body": "After v2.4.1 update, the app crashes immediately on launch...",
  "comments": []
}
```

**Output:**

```json
{
  "summary": "Application crashes on startup since v2.4.1 with a SIGSEGV signal, reproducible when GPU memory exceeds 8GB. The issue is confirmed to be a regression — v2.4.0 is unaffected.",
  "type": "bug",
  "labels": ["bug", "crash"],
  "confidence": 0.94,
  "similar_issues": [
    { "id": 209831, "score": 0.81 },
    { "id": 208104, "score": 0.57 }
  ],
  "reply": "Thanks for the detailed report and the version bisect — that's super helpful. This looks like a GPU memory management regression in v2.4.1. We'll investigate and prioritize a patch."
}
```

<br/>

---

## AI Backends

### OpenAI *(default)*

Fast, accurate, costs fractions of a cent per issue.

```env
OPENAI_API_KEY=sk-...
ISSUESHERIFF_MODEL=gpt-4o-mini   # default — fast and cheap
# ISSUESHERIFF_MODEL=gpt-4o      # for higher accuracy
```

### Ollama *(fully offline)*

No API key. No data leaving your machine. Works air-gapped.

```bash
ollama run mistral   # or llama3, qwen2.5, etc.
```

```env
OLLAMA_MODEL=mistral
OLLAMA_BASE_URL=http://localhost:11434
```

### No AI

If no backend is configured, IssueSheriff still runs — heuristic classification and TF-IDF duplicate detection work entirely without an API key.

```bash
issuesheriff scan myorg/myrepo --no-reply   # duplicates work, AI features skipped
```

<br/>

---

## Configuration

All settings via `.env` or environment variables:

| Variable | Default | Description |
|:--|:--|:--|
| `GITHUB_TOKEN` | — | GitHub PAT — needs `repo` read + `issues` write |
| `OPENAI_API_KEY` | — | OpenAI API key |
| `ISSUESHERIFF_MODEL` | `gpt-4o-mini` | OpenAI model to use |
| `OLLAMA_MODEL` | — | Ollama model name (activates local mode) |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL |
| `SIMILARITY_THRESHOLD` | `0.45` | Min score to report as duplicate (0.0–1.0) |
| `MAX_ISSUES` | `100` | Max issues fetched per `scan` |

<br/>

---

## Development

```bash
git clone https://github.com/yourusername/issuesheriff
cd issuesheriff
pip install -e ".[dev,similarity]"
pytest
```

```
tests/test_core.py ............. 13 passed in 3.68s
```

**Project structure:**

```
issuesheriff/
├── issuesheriff/
│   ├── main.py           CLI — typer + rich
│   ├── ai.py             OpenAI / Ollama / heuristic fallback
│   ├── github_client.py  GitHub REST API with pagination
│   ├── similarity.py     TF-IDF + cosine (sklearn or pure-Python)
│   ├── config.py         dotenv configuration
│   └── utils.py          shared helpers
├── tests/
│   └── test_core.py
├── examples/
│   └── sample_issue.json
├── .github/workflows/
│   └── triage.yml        GitHub Action
├── .env.example
└── pyproject.toml
```

**Contributing:**

1. Fork → branch → PR
2. Run `pytest` before submitting
3. `ruff check .` for linting
4. Issues and feature requests welcome

<br/>

---

## Roadmap

- [ ] GitHub App — webhook-based, zero config for org-wide deployment
- [ ] `sentence-transformers` backend for better semantic similarity
- [ ] Stale issue detection and auto-close suggestions
- [ ] Web dashboard — per-repo analytics and triage queue
- [ ] Discord / Telegram / Slack notifications
- [ ] Issue velocity and resolution time analytics
- [ ] `--dry-run` mode for all write operations

<br/>

---

## License

MIT © IssueSheriff Contributors — see [LICENSE](LICENSE)

<br/>

---

<div align="center">

**[PyPI](https://pypi.org/project/issuesheriff/) · [Issues](https://github.com/yourusername/issuesheriff/issues) · [Discussions](https://github.com/yourusername/issuesheriff/discussions)**

<br/>

<sub>Built for maintainers who have better things to do than triage 200 issues by hand.</sub>

</div>
