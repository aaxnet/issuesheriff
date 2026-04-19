[RU](README.ru.md) | [USA](README.md)
<div align="center">

```
 ██╗███████╗███████╗██╗   ██╗███████╗███████╗██╗  ██╗███████╗██████╗ ██╗███████╗███████╗
 ██║██╔════╝██╔════╝██║   ██║██╔════╝██╔════╝██║  ██║██╔════╝██╔══██╗██║██╔════╝██╔════╝
 ██║███████╗███████╗██║   ██║█████╗  ███████╗███████║█████╗  ██████╔╝██║█████╗  █████╗  
 ██║╚════██║╚════██║██║   ██║██╔══╝  ╚════██║██╔══██║██╔══╝  ██╔══██╗██║██╔══╝  ██╔══╝  
 ██║███████║███████║╚██████╔╝███████╗███████║██║  ██║███████╗██║  ██║██║██║     ██║     
 ╚═╝╚══════╝╚══════╝ ╚═════╝ ╚══════╝╚══════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝╚═╝     ╚═╝   
```

**AI-powered GitHub issue triage — in your terminal, in seconds.**

<br/>

[![PyPI](https://img.shields.io/pypi/v/issuesheriff?style=flat-square&color=black)](https://pypi.org/project/issuesheriff/)
[![Python](https://img.shields.io/badge/python-3.10+-black?style=flat-square)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-black?style=flat-square)](LICENSE)
[![CI](https://img.shields.io/github/actions/workflow/status/aaxnet/issuesheriff/tests.yml?style=flat-square&color=black)](https://github.com/aaxnet/issuesheriff/actions)
[![Downloads](https://img.shields.io/pypi/dm/issuesheriff?style=flat-square&color=black)](https://pypi.org/project/issuesheriff/)

<br/>

<!-- Replace with your GIF -->
<img src="demo.gif" alt="IssueSheriff demo" width="740"/>

<br/><br/>

</div>

---

## The problem

You open your repo after a weekend. **47 new issues.** Duplicates, vague bug reports, feature requests disguised as bugs, questions that belong in Discussions. You spend an hour just reading and labeling.

**IssueSheriff fixes that.**

One command scans your entire issue tracker, classifies every issue, spots duplicates, suggests labels, and drafts ready-to-send replies — in the time it takes to make coffee.

---

## Install

```bash
pip install issuesheriff
```

> Works out of the box without an API key. AI features activate automatically when `OPENAI_API_KEY` is set.

---

## 30-second quickstart

```bash
# 1. Set your tokens
export GITHUB_TOKEN=ghp_...
export OPENAI_API_KEY=sk-...      # optional — enables AI replies & smarter classification

# 2. Scan any repo
issuesheriff scan aaxnet/issuesheriff

# 3. Suggest + apply labels on a specific issue
issuesheriff labels aaxnet/issuesheriff 42 --apply

# 4. Draft a maintainer reply and copy it to clipboard
issuesheriff reply aaxnet/issuesheriff 42 --copy
```

That's it.

---

## What it does

| Command | What happens |
|---|---|
| `scan <owner/repo>` | Reads all open issues, classifies them, flags duplicates, prints a clean summary |
| `analyze <file.json>` | Deep-analyzes a single issue — type, labels, confidence score, similar issues, reply draft |
| `labels <owner/repo> <#>` | Suggests labels for one issue; `--apply` writes them to GitHub |
| `reply <owner/repo> <#>` | Generates a human-sounding maintainer reply; `--copy` puts it in your clipboard |

---

## Output that's actually useful

Run `issuesheriff scan microsoft/vscode --limit 50` and you get:

```
┌─────────────────────────────────────────────────────────────────┐
│  Scanned 50 issues  ·  microsoft/vscode  ·  3.2s               │
├──────┬──────────────────────────────────────┬────────┬──────────┤
│  #   │  Title                               │  Type  │  Labels  │
├──────┼──────────────────────────────────────┼────────┼──────────┤
│  209 │  Extension host crashes on startup   │  bug   │ bug,crash│
│  208 │  Add vim keybindings to terminal     │  feat  │ feature  │
│  207 │  How do I change the default shell?  │  docs  │ question │
│  206 │  [DUP] Terminal not opening  ──→ #201│  dup   │ duplicate│
└──────┴──────────────────────────────────────┴────────┴──────────┘

  Bugs: 21   Features: 14   Questions: 9   Duplicates: 6
```

And `issuesheriff analyze issue.json` returns structured JSON you can pipe anywhere:

```json
{
  "summary": "Application crashes immediately on launch after the latest update.",
  "type": "bug",
  "labels": ["bug", "crash", "regression"],
  "confidence": 0.94,
  "similar_issues": [
    { "id": 209831, "score": 0.81 },
    { "id": 208104, "score": 0.57 }
  ],
  "reply": "Thanks for the report — this looks like a crash regression introduced recently. We'll investigate and keep you posted here."
}
```

---

## Automate it with GitHub Actions

Drop this in `.github/workflows/triage.yml` and every new issue gets triaged automatically:

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

## AI backends

IssueSheriff works with three backends — pick what fits your stack.

### OpenAI (default)
Best accuracy, easiest setup:
```env
OPENAI_API_KEY=sk-...
ISSUESHERIFF_MODEL=gpt-4o-mini   # cheap and fast; swap for gpt-4o if you need it
```

### Ollama — fully offline
No data leaves your machine:
```bash
ollama run mistral
```
```env
OLLAMA_MODEL=mistral
OLLAMA_BASE_URL=http://localhost:11434
```

### No AI
If no key is configured, IssueSheriff still runs — heuristic classification + TF-IDF duplicate detection work without any API:
```bash
issuesheriff scan aaxnet/issuesheriff --no-reply
```

---

## Configuration

| Variable | Default | Description |
|---|---|---|
| `GITHUB_TOKEN` | — | GitHub token with `issues: write` |
| `OPENAI_API_KEY` | — | OpenAI key (optional) |
| `ISSUESHERIFF_MODEL` | `gpt-4o-mini` | OpenAI model |
| `OLLAMA_MODEL` | — | Local Ollama model name |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server |
| `SIMILARITY_THRESHOLD` | `0.45` | Cosine similarity threshold for duplicates |
| `MAX_ISSUES` | `100` | Max issues fetched per scan |

---

## Install options

```bash
# Core only
pip install issuesheriff

# + duplicate detection (TF-IDF cosine similarity)
pip install "issuesheriff[similarity]"

# + Ollama support
pip install "issuesheriff[similarity,ollama]"

# Full dev setup
pip install "issuesheriff[similarity,ollama,dev]"
```

---

## Project structure

```
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

## Developing locally

```bash
git clone https://github.com/aaxnet/issuesheriff
cd issuesheriff
pip install -e ".[dev,similarity]"
pytest
ruff check .
```

PRs welcome. Check [open issues](https://github.com/aaxnet/issuesheriff/issues) for good first tasks.

---

<div align="center">

**If IssueSheriff saved you time, a ⭐ helps others find it.**

[PyPI](https://pypi.org/project/issuesheriff/) · [Report a bug](https://github.com/aaxnet/issuesheriff/issues/new) · [Request a feature](https://github.com/aaxnet/issuesheriff/issues/new)

</div>
