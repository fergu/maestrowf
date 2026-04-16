from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def run(cmd: list[str], cwd: Path) -> None:
    print(f"+ {' '.join(cmd)}")
    subprocess.run(cmd, cwd=cwd, check=True)


def prepare_docs_changelog(repo_root: Path, mode: str, title: str | None = None) -> None:
    changelog = repo_root / "CHANGELOG.md"
    docs_changelog = repo_root / "CHANGELOG_docs.md"
    scriv_config = repo_root / "scriv_docs.ini" # SHould we put this in scripts too to avoid clutter?

    if not changelog.exists():
        raise FileNotFoundError(f"Missing source changelog: {changelog}")

    print(f"Copying {changelog} -> {docs_changelog}")
    shutil.copyfile(changelog, docs_changelog)

    if mode == "dev":
        cmd = [
            "scriv",
            "collect",
            "--keep",
            "--config",
            str(scriv_config),
        ]
        if title:
            cmd.extend(["--title", title])

        run(cmd, cwd=repo_root)
    elif mode == "release":
        print("Release mode selected, using copied CHANGELOG.md without scriv collect.")
    else:
        raise ValueError(f"Unknown mode: {mode}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Prepare docs changelog for MkDocs builds."
    )
    parser.add_argument(
        "--mode",
        choices=["dev", "release"],
        required=True,
        help="dev = include unreleased fragments, release = use committed changelog only",
    )
    parser.add_argument(
        "--title",
        default="Unreleased",
        help="Title to use for scriv collect in dev mode",
    )

    args = parser.parse_args()
    repo_root = Path(__file__).resolve().parent.parent
    print(f"Running with interpreter at '{sys.executable}'")
    try:
        prepare_docs_changelog(repo_root, mode=args.mode, title=args.title)
    except subprocess.CalledProcessError as exc:
        print(f"Command failed with exit code {exc.returncode}", file=sys.stderr)
        return exc.returncode
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print("Docs changelog prepared successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
