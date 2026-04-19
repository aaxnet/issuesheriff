"""
IssueSheriff — AI-powered GitHub Issue triage tool.
"""

import json
import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.text import Text
from rich import box

from issuesheriff import __version__
from issuesheriff.ai import analyze_issue, generate_reply, suggest_labels
from issuesheriff.github_client import GitHubClient
from issuesheriff.similarity import find_duplicates
from issuesheriff.config import get_config, save_user_config, load_existing_user_config, USER_CONFIG_FILE
from issuesheriff.utils import format_score_bar, truncate

app = typer.Typer(
    name="issuesheriff",
    help="🔍 AI-powered GitHub Issue triage. Analyze, label, deduplicate, reply.",
    add_completion=False,
    rich_markup_mode="rich",
)
console = Console()


def version_callback(value: bool):
    if value:
        console.print(f"[bold cyan]IssueSheriff[/] v{__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        None, "--version", "-v", callback=version_callback, is_eager=True,
        help="Show version and exit."
    )
):
    pass


# ─────────────────────────────────────────────
#  issuesheriff analyze <file>
# ─────────────────────────────────────────────
@app.command()
def analyze(
    file: Path = typer.Argument(..., help="Path to issue JSON file"),
    json_output: bool = typer.Option(False, "--json", help="Output raw JSON"),
    no_reply: bool = typer.Option(False, "--no-reply", help="Skip reply generation"),
):
    """
    🔍 Analyze a local issue JSON file.

    \b
    Expected format:
      { "title": "...", "body": "...", "comments": [] }
    """
    if not file.exists():
        console.print(f"[red]✗[/] File not found: {file}")
        raise typer.Exit(1)

    try:
        issue = json.loads(file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        console.print(f"[red]✗[/] Invalid JSON: {e}")
        raise typer.Exit(1)

    _run_analysis(issue, json_output=json_output, include_reply=not no_reply)


# ─────────────────────────────────────────────
#  issuesheriff scan <owner/repo>
# ─────────────────────────────────────────────
@app.command()
def scan(
    repo: str = typer.Argument(..., help="GitHub repo in owner/repo format"),
    limit: int = typer.Option(20, "--limit", "-n", help="Max issues to fetch"),
    state: str = typer.Option("open", "--state", help="Issue state: open / closed / all"),
    json_output: bool = typer.Option(False, "--json", help="Output raw JSON"),
    duplicates: bool = typer.Option(True, "--duplicates/--no-duplicates", help="Run duplicate detection"),
):
    """
    📡 Fetch & analyze issues from a GitHub repository.

    \b
    Example:
      issuesheriff scan microsoft/vscode --limit 10
    """
    if not _check_token_or_hint():
        raise typer.Exit(1)
    config = get_config()
    client = GitHubClient(config.github_token)

    with Progress(
        SpinnerColumn(spinner_name="dots"),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task(f"Fetching issues from [cyan]{repo}[/]...", total=None)
        issues = client.get_issues(repo, state=state, limit=limit)
        progress.update(task, description=f"Fetched [cyan]{len(issues)}[/] issues")

    if not issues:
        console.print("[yellow]⚠[/] No issues found.")
        raise typer.Exit()

    _print_repo_banner(repo, len(issues))

    results = []
    for i, issue in enumerate(issues, 1):
        console.rule(f"[dim]Issue #{issue.get('number', i)}[/]")
        result = _run_analysis(
            issue,
            issue_number=issue.get("number"),
            json_output=False,
            include_reply=False,
            compact=True,
        )
        results.append(result)

    if duplicates and len(issues) > 1:
        console.rule("[bold]Duplicate Detection[/]")
        _run_duplicate_scan(issues)

    if json_output:
        console.print_json(json.dumps(results, ensure_ascii=False, indent=2))


# ─────────────────────────────────────────────
#  issuesheriff reply <issue_id>
# ─────────────────────────────────────────────
@app.command()
def reply(
    repo: str = typer.Argument(..., help="GitHub repo in owner/repo format"),
    issue_id: int = typer.Argument(..., help="Issue number"),
    copy: bool = typer.Option(False, "--copy", "-c", help="Copy reply to clipboard"),
):
    """
    💬 Generate a maintainer reply draft for an issue.

    \b
    Example:
      issuesheriff reply microsoft/vscode 12345
    """
    if not _check_token_or_hint():
        raise typer.Exit(1)
    config = get_config()
    client = GitHubClient(config.github_token)

    with Progress(SpinnerColumn(), TextColumn("{task.description}"), console=console, transient=True) as p:
        p.add_task(f"Fetching issue #{issue_id}...", total=None)
        issue = client.get_issue(repo, issue_id)

    with Progress(SpinnerColumn(), TextColumn("{task.description}"), console=console, transient=True) as p:
        p.add_task("Generating reply...", total=None)
        draft = generate_reply(issue["title"], issue.get("body", ""))

    console.print(Panel(
        draft,
        title=f"[bold green]Reply Draft — #{issue_id}[/]",
        border_style="green",
        padding=(1, 2),
    ))

    if copy:
        try:
            import pyperclip
            pyperclip.copy(draft)
            console.print("[dim]✓ Copied to clipboard[/]")
        except ImportError:
            console.print("[yellow]⚠[/] Install pyperclip for --copy support")


# ─────────────────────────────────────────────
#  issuesheriff labels <issue_id>
# ─────────────────────────────────────────────
@app.command()
def labels(
    repo: str = typer.Argument(..., help="GitHub repo in owner/repo format"),
    issue_id: int = typer.Argument(..., help="Issue number"),
    apply: bool = typer.Option(False, "--apply", "-a", help="Apply labels via GitHub API"),
):
    """
    🏷  Suggest (or apply) labels for an issue.

    \b
    Example:
      issuesheriff labels microsoft/vscode 12345 --apply
    """
    if not _check_token_or_hint():
        raise typer.Exit(1)
    config = get_config()
    client = GitHubClient(config.github_token)

    with Progress(SpinnerColumn(), TextColumn("{task.description}"), console=console, transient=True) as p:
        p.add_task(f"Fetching issue #{issue_id}...", total=None)
        issue = client.get_issue(repo, issue_id)

    with Progress(SpinnerColumn(), TextColumn("{task.description}"), console=console, transient=True) as p:
        p.add_task("Analyzing labels...", total=None)
        suggested = suggest_labels(issue["title"], issue.get("body", ""))

    table = Table(box=box.ROUNDED, show_header=True, header_style="bold cyan")
    table.add_column("Label", style="bold")
    table.add_column("Confidence", justify="right")

    for label, confidence in suggested.items():
        bar = format_score_bar(confidence)
        table.add_row(f"[magenta]{label}[/]", f"{bar} {confidence:.0%}")

    console.print(Panel(table, title=f"[bold]Suggested Labels — #{issue_id}[/]", border_style="cyan"))

    if apply:
        label_names = list(suggested.keys())
        client.apply_labels(repo, issue_id, label_names)
        console.print(f"[green]✓[/] Applied: {', '.join(label_names)}")



# ─────────────────────────────────────────────
#  issuesheriff setup
# ─────────────────────────────────────────────
@app.command()
def setup():
    """
    ⚙️  Interactive first-run (or re-run) configuration wizard.

    \b
    Saves tokens and settings to ~/.config/issuesheriff/.env
    so you never have to export env vars manually.
    """
    existing = load_existing_user_config()
    is_update = bool(existing)

    console.print()
    console.print(Panel(
        "[bold cyan]IssueSheriff Setup Wizard[/]\n"
        "[dim]Answers saved to [/][cyan]~/.config/issuesheriff/.env[/]\n"
        "[dim]Press Enter to keep the current value shown in brackets.[/]",
        border_style="cyan",
        padding=(1, 2),
    ))
    console.print()

    def _ask(label, key, secret=False, hint=""):
        current = existing.get(key, "")
        display = ("*" * min(len(current), 8) + current[-4:]) if secret and current else current
        parts = f"  [bold]{label}[/]"
        if hint:
            parts += f" [dim]({hint})[/]"
        if display:
            parts += f" [dim][{display}][/]"
        parts += ": "
        console.print(parts, end="")
        value = input()
        return value.strip() or current

    console.rule("[dim]Required[/]")
    github_token = _ask("GitHub Token", "GITHUB_TOKEN", secret=True,
                        hint="github.com/settings/tokens — repo + issues:write")

    console.print()
    console.rule("[dim]AI Backend  (both optional)[/]")
    console.print("  [dim]OpenAI = cloud accuracy   Ollama = local privacy[/]\n")

    openai_key = _ask("OpenAI API Key", "OPENAI_API_KEY", secret=True,
                      hint="platform.openai.com/api-keys — blank to skip")
    openai_model = ""
    if openai_key:
        openai_model = _ask("OpenAI model", "ISSUESHERIFF_MODEL", hint="default: gpt-4o-mini")

    ollama_model = _ask("Ollama model", "OLLAMA_MODEL", hint="e.g. mistral — blank to skip")
    ollama_url = ""
    if ollama_model:
        ollama_url = _ask("Ollama base URL", "OLLAMA_BASE_URL", hint="default: http://localhost:11434")

    console.print()
    console.rule("[dim]Tuning (optional)[/]")
    similarity = _ask("Duplicate threshold", "SIMILARITY_THRESHOLD", hint="0.0–1.0, default 0.45")
    max_issues = _ask("Max issues per scan", "MAX_ISSUES", hint="default 100")

    values = {k: v for k, v in {
        "GITHUB_TOKEN": github_token,
        "OPENAI_API_KEY": openai_key,
        "ISSUESHERIFF_MODEL": openai_model,
        "OLLAMA_MODEL": ollama_model,
        "OLLAMA_BASE_URL": ollama_url,
        "SIMILARITY_THRESHOLD": similarity,
        "MAX_ISSUES": max_issues,
    }.items() if v}

    saved_path = save_user_config(values)

    console.print()
    verb = "Updated" if is_update else "Saved"
    console.print(Panel(
        f"[green]✓[/] {verb}: [cyan]{saved_path}[/]\n\n"
        "[dim]Run [/][bold]issuesheriff scan <owner/repo>[/][dim] to get started.[/]",
        border_style="green",
        padding=(1, 2),
    ))
    console.print()


def _check_token_or_hint() -> bool:
    """Returns True if token is set, else prints setup hint and returns False."""
    config = get_config()
    if config.github_token:
        return True
    console.print(
        "\n[red]✗[/] [bold]GITHUB_TOKEN[/] is not set.\n\n"
        "  Run [bold cyan]issuesheriff setup[/] to configure it interactively,\n"
        "  or export it manually:\n"
        "    [dim]export GITHUB_TOKEN=ghp_...[/]\n"
    )
    return False


# ─────────────────────────────────────────────
#  Internal helpers
# ─────────────────────────────────────────────

def _run_analysis(issue: dict, issue_number: int = None, json_output: bool = False,
                  include_reply: bool = True, compact: bool = False) -> dict:
    title = issue.get("title", "(no title)")
    body = issue.get("body", "")

    with Progress(SpinnerColumn(), TextColumn("{task.description}"), console=console, transient=True) as p:
        p.add_task("Analyzing with AI...", total=None)
        result = analyze_issue(title, body)

    if include_reply and not compact:
        with Progress(SpinnerColumn(), TextColumn("{task.description}"), console=console, transient=True) as p:
            p.add_task("Generating reply draft...", total=None)
            result["reply"] = generate_reply(title, body)

    if json_output:
        console.print_json(json.dumps(result, ensure_ascii=False, indent=2))
        return result

    _print_analysis(title, result, issue_number=issue_number, compact=compact)
    return result


def _print_analysis(title: str, result: dict, issue_number: int = None, compact: bool = False):
    num_str = f"[dim]#{issue_number}[/] " if issue_number else ""

    # Header
    type_colors = {"bug": "red", "feature": "blue", "question": "yellow", "docs": "cyan"}
    issue_type = result.get("type", "unknown")
    color = type_colors.get(issue_type, "white")
    type_badge = f"[bold {color}][{issue_type.upper()}][/]"

    console.print(f"\n  {num_str}[bold]{truncate(title, 70)}[/] {type_badge}")

    # Summary
    console.print(f"\n  [dim]Summary[/]")
    console.print(f"  {result.get('summary', '')}\n")

    # Labels
    label_list = result.get("labels", [])
    if label_list:
        label_str = "  ".join(f"[on {type_colors.get(l, 'white')} bold] {l} [/]" for l in label_list)
        console.print(f"  [dim]Labels[/]  {label_str}\n")

    # Reply (full mode only)
    if "reply" in result and not compact:
        console.print(Panel(
            result["reply"],
            title="[bold green]Reply Draft[/]",
            border_style="green",
            padding=(1, 2),
        ))


def _run_duplicate_scan(issues: list):
    with Progress(SpinnerColumn(), TextColumn("{task.description}"), console=console, transient=True) as p:
        p.add_task("Running similarity analysis...", total=None)
        pairs = find_duplicates(issues)

    if not pairs:
        console.print("  [green]✓[/] No significant duplicates found.\n")
        return

    table = Table(box=box.SIMPLE, show_header=True, header_style="bold")
    table.add_column("Issue A", style="cyan")
    table.add_column("Issue B", style="cyan")
    table.add_column("Similarity", justify="right")

    for pair in pairs[:10]:
        bar = format_score_bar(pair["score"])
        a = f"#{pair['a']} {truncate(pair['title_a'], 35)}"
        b = f"#{pair['b']} {truncate(pair['title_b'], 35)}"
        table.add_row(a, b, f"{bar} {pair['score']:.0%}")

    console.print(table)


def _print_repo_banner(repo: str, count: int):
    text = Text()
    text.append("  📦 ", style="")
    text.append(repo, style="bold cyan")
    text.append(f"  —  {count} issues loaded", style="dim")
    console.print(Panel(text, border_style="dim", padding=(0, 1)))
    console.print()


if __name__ == "__main__":
    app()
