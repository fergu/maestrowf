"""Generate the changelog page consumed by the MkDocs build.

This script writes ``whats_new/changelog.md`` from changelog content found
at the repository root. It prefers ``CHANGELOG_docs.md`` when present, then
falls back to ``CHANGELOG.md``. If neither file exists, it writes a
placeholder page so the documentation build can still succeed.
"""

from pathlib import Path

import mkdocs_gen_files


REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS_CHANGELOG = REPO_ROOT / "CHANGELOG_docs.md"
BASE_CHANGELOG = REPO_ROOT / "CHANGELOG.md"
OUTPUT_PATH = "whats_new/changelog.md"
# TODO: might need to adopt the hook that copier distributes to handle links to changelog:
#       https://github.com/copier-org/copier


def get_changelog_content() -> str:
    """Return changelog content for documentation generation.

    The function first reads ``CHANGELOG_docs.md`` from the repository root
    when it exists. If that file is not available, it falls back to
    ``CHANGELOG.md``. If neither file is present, it returns a placeholder
    Markdown document so the MkDocs build can continue without failing.

    Returns:
        str: Markdown content for the generated changelog page.
    """
    if DOCS_CHANGELOG.exists():
        return DOCS_CHANGELOG.read_text(encoding="utf-8")

    if BASE_CHANGELOG.exists():
        return BASE_CHANGELOG.read_text(encoding="utf-8")

    return """# Changelog

No changelog is available yet.

If you expected development changelog content here, generate `CHANGELOG_docs.md` before building the documentation.
"""


with mkdocs_gen_files.open(OUTPUT_PATH, "w") as fd:
    fd.write(get_changelog_content())
