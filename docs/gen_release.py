"""Generate the release-process page for the MkDocs site.

This script writes ``whats_new/release.md`` using ``RELEASE.md`` from the
repository root when it is available. If the source file does not exist, it
writes a placeholder page instead.
"""

from pathlib import Path

import mkdocs_gen_files


REPO_ROOT = Path(__file__).resolve().parent.parent
SOURCE = REPO_ROOT / "RELEASE.md"
OUTPUT_PATH = "whats_new/release.md"


def get_release_content() -> str:
    """Return release-process content for documentation generation."""
    if SOURCE.exists():
        return SOURCE.read_text(encoding="utf-8")

    return "# Release Process\n\nRelease process guide not found.\n"


with mkdocs_gen_files.open(OUTPUT_PATH, "w") as fd:
    fd.write(get_release_content())

if SOURCE.exists():
    mkdocs_gen_files.set_edit_path(OUTPUT_PATH, SOURCE)
