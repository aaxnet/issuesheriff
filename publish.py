from __future__ import annotations

import argparse
import getpass
import os
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def run(cmd: list[str], env: dict[str, str] | None = None) -> None:
    print(f"\n> {' '.join(cmd)}")
    subprocess.run(cmd, cwd=ROOT, env=env, check=True)


def clean() -> None:
    for name in ("dist", "build", "issuesheriff.egg-info"):
        path = ROOT / name
        if path.exists():
            shutil.rmtree(path, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build and upload package to PyPI.")
    parser.add_argument(
        "--repository",
        default="pypi",
        help="Upload target: pypi or testpypi (default: pypi)",
    )
    parser.add_argument(
        "--skip-clean",
        action="store_true",
        help="Do not remove dist/build/*.egg-info before building",
    )
    args = parser.parse_args()

    pyproject = ROOT / "pyproject.toml"
    if not pyproject.exists():
        print("pyproject.toml not found in project root.")
        return 1

    if not args.skip_clean:
        clean()

    env = os.environ.copy()

    token = env.get("TWINE_PASSWORD") or env.get("PYPI_TOKEN")
    if not token:
        token = getpass.getpass("PyPI token: ").strip()

    if not token:
        print("No token provided.")
        return 1

    env["TWINE_USERNAME"] = "__token__"
    env["TWINE_PASSWORD"] = token

    run([sys.executable, "-m", "build"], env=env)
    run([sys.executable, "-m", "twine", "check", "dist/*"], env=env)
    run([sys.executable, "-m", "twine", "upload", "--repository", args.repository, "dist/*"], env=env)

    print("\nDone.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())