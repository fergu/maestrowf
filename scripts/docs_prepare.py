"""Prepare the documentation-specific changelog for MkDocs builds.

This script creates ``CHANGELOG_docs.md`` from the repository changelog and,
in development mode, optionally augments it with unreleased Scriv fragments.
It is intended to support documentation builds that need a changelog tailored
for published docs content.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def run(cmd: list[str], cwd: Path) -> None:
    """Run a subprocess command in the given working directory.

    The command is printed before execution to make build output easier to
    inspect when troubleshooting failures.

    Args:
        cmd: Command and arguments to execute.
        cwd: Working directory in which to run the command.

    Raises:
        subprocess.CalledProcessError: If the command exits with a nonzero
            status code.
    """
    print(f"+ {' '.join(cmd)}")
    subprocess.run(cmd, cwd=cwd, check=True)


def has_changelog_fragments(fragment_dir: Path) -> bool:
    """Return whether Scriv has Markdown fragments to collect."""
    return fragment_dir.exists() and any(fragment_dir.glob("*.md"))


def prepare_docs_changelog(repo_root: Path, mode: str, title: str | None = None) -> None:
    """Create the changelog file used by the documentation build.

    The function copies ``CHANGELOG.md`` to ``CHANGELOG_docs.md`` in the
    repository root. In ``dev`` mode, it then runs ``scriv collect`` with the
    documentation-specific configuration so unreleased fragments can be
    included in the generated docs changelog. In ``release`` mode, it leaves
    the copied changelog unchanged.

    Args:
        repo_root (Path): Path to the repository root.
        mode (str): Changelog preparation mode, either ``"dev"`` or ``"release"``.
        title (str): Optional section title passed to ``scriv collect`` in
            development mode.

    Raises:
        FileNotFoundError: If ``CHANGELOG.md`` does not exist.
        ValueError: If ``mode`` is not recognized.
        subprocess.CalledProcessError: If the Scriv command fails.
    """
    changelog = repo_root / "CHANGELOG.md"
    docs_changelog = repo_root / "CHANGELOG_docs.md"
    # TODO: Consider moving this into scripts too to avoid repo-root clutter?
    scriv_config = repo_root / "scriv_docs.ini"
    fragment_dir = repo_root / "changelog.d"

    if not changelog.exists():
        raise FileNotFoundError(f"Missing source changelog: {changelog}")

    print(f"Copying {changelog} -> {docs_changelog}")
    shutil.copyfile(changelog, docs_changelog)

    if mode == "dev":
        if not has_changelog_fragments(fragment_dir):
            print(
                f"No changelog fragments found in {fragment_dir}; "
                "skipping scriv collect."
            )
            return

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
    """Parse arguments and prepare the docs changelog.

    Returns:
        Process exit code, where ``0`` indicates success and nonzero values
        indicate failure.
    """
    parser = argparse.ArgumentParser(
        description="Prepare changelog used by MkDocs builds."
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
