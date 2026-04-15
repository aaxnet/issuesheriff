"""
Configuration — loads from environment / .env file.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from functools import lru_cache


@dataclass
class Config:
    github_token: str = ""
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    ollama_model: str = ""
    ollama_base_url: str = "http://localhost:11434"
    similarity_threshold: float = 0.45
    max_issues: int = 100


@lru_cache(maxsize=1)
def get_config() -> Config:
    """
    Load config from environment.
    Respects .env file if python-dotenv is installed.
    """
    _try_load_dotenv()

    return Config(
        github_token=os.getenv("GITHUB_TOKEN", ""),
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        openai_model=os.getenv("ISSUESHERIFF_MODEL", "gpt-4o-mini"),
        ollama_model=os.getenv("OLLAMA_MODEL", ""),
        ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        similarity_threshold=float(os.getenv("SIMILARITY_THRESHOLD", "0.45")),
        max_issues=int(os.getenv("MAX_ISSUES", "100")),
    )


def _try_load_dotenv() -> None:
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
