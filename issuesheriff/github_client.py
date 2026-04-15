"""
GitHub API client — issues, labels, pagination.
"""

from __future__ import annotations

import logging
from typing import Iterator

import httpx

logger = logging.getLogger(__name__)

GITHUB_API = "https://api.github.com"


class GitHubClient:
    def __init__(self, token: str | None = None):
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"

        self._client = httpx.Client(
            base_url=GITHUB_API,
            headers=headers,
            timeout=30,
        )

    # ─────────────────────────────────────────────
    #  Issues
    # ─────────────────────────────────────────────

    def get_issues(
        self,
        repo: str,
        state: str = "open",
        limit: int = 50,
    ) -> list[dict]:
        """Fetch up to `limit` issues from a repo (excludes PRs)."""
        issues = []
        for issue in self._paginate(f"/repos/{repo}/issues", params={"state": state, "per_page": 100}):
            if "pull_request" in issue:
                continue  # Skip PRs
            issues.append(issue)
            if len(issues) >= limit:
                break
        return issues

    def get_issue(self, repo: str, issue_number: int) -> dict:
        """Fetch a single issue."""
        r = self._client.get(f"/repos/{repo}/issues/{issue_number}")
        self._raise(r)
        return r.json()

    # ─────────────────────────────────────────────
    #  Labels
    # ─────────────────────────────────────────────

    def get_repo_labels(self, repo: str) -> list[str]:
        """List all labels in a repo."""
        labels = []
        for label in self._paginate(f"/repos/{repo}/labels"):
            labels.append(label["name"])
        return labels

    def apply_labels(self, repo: str, issue_number: int, labels: list[str]) -> None:
        """Apply labels to an issue (creates missing labels automatically)."""
        existing = set(self.get_repo_labels(repo))
        for label in labels:
            if label not in existing:
                self._create_label(repo, label)

        r = self._client.post(
            f"/repos/{repo}/issues/{issue_number}/labels",
            json={"labels": labels},
        )
        self._raise(r)

    def _create_label(self, repo: str, name: str, color: str = "ededed") -> None:
        self._client.post(
            f"/repos/{repo}/labels",
            json={"name": name, "color": color},
        )

    # ─────────────────────────────────────────────
    #  Pull Requests
    # ─────────────────────────────────────────────

    def get_pull_requests(self, repo: str, state: str = "open", limit: int = 50) -> list[dict]:
        """Fetch open PRs."""
        prs = []
        for pr in self._paginate(f"/repos/{repo}/pulls", params={"state": state, "per_page": 100}):
            prs.append(pr)
            if len(prs) >= limit:
                break
        return prs

    # ─────────────────────────────────────────────
    #  Internals
    # ─────────────────────────────────────────────

    def _paginate(self, path: str, params: dict | None = None) -> Iterator[dict]:
        url = path
        p = dict(params or {})
        p.setdefault("per_page", 100)

        while url:
            r = self._client.get(url, params=p if "?" not in url else None)
            self._raise(r)
            data = r.json()
            if isinstance(data, list):
                yield from data
            else:
                yield data
                return

            # Follow Link: <next> header
            link = r.headers.get("Link", "")
            url = self._parse_next_link(link)
            p = {}  # Params embedded in next URL

    @staticmethod
    def _parse_next_link(link_header: str) -> str | None:
        for part in link_header.split(","):
            if 'rel="next"' in part:
                url = part.split(";")[0].strip().strip("<>")
                return url
        return None

    @staticmethod
    def _raise(response: httpx.Response) -> None:
        if response.status_code == 401:
            raise PermissionError("GitHub API: Unauthorized. Check your GITHUB_TOKEN.")
        if response.status_code == 403:
            raise PermissionError("GitHub API: Forbidden. Rate limit or insufficient permissions.")
        if response.status_code == 404:
            raise FileNotFoundError(f"GitHub API: Not found — {response.url}")
        if response.status_code >= 400:
            raise RuntimeError(f"GitHub API error {response.status_code}: {response.text[:200]}")

    def __del__(self):
        try:
            self._client.close()
        except Exception:
            pass
