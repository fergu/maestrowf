"""Generate the contributing page for the MkDocs site.

This script writes ``whats_new/contributing.md`` using ``CONTRIBUTING.md``
from the repository root when it is available. If the source file does not
exist, it writes a placeholder page instead. When a source file is present,
the generated page is also linked back to it as the edit path.
"""

from pathlib import Path

import mkdocs_gen_files


REPO_ROOT = Path(__file__).resolve().parent.parent
SOURCE = REPO_ROOT / "CONTRIBUTING.md"
OUTPUT_PATH = "whats_new/contributing.md"

def get_contributing_content() -> str:
    """Return contributing guide content for documentation generation.

    The function reads ``CONTRIBUTING.md`` from the repository root when it
    exists. If the file is missing, it returns a placeholder Markdown
    document so the MkDocs build can continue without failing.

    Returns:
        Markdown content for the generated contributing page.
    """
    if SOURCE.exists():
        return SOURCE.read_text(encoding="utf-8")

    return "# Contributing\n\nContributor guide not found.\n"


with mkdocs_gen_files.open(OUTPUT_PATH, "w") as fd:
    fd.write(get_contributing_content())
    
if SOURCE.exists():
    mkdocs_gen_files.set_edit_path(OUTPUT_PATH, SOURCE)
