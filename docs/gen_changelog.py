from pathlib import Path

import mkdocs_gen_files


repo_root = Path(__file__).resolve().parent.parent
docs_changelog = repo_root / "CHANGELOG_docs.md"
base_changelog = repo_root / "CHANGELOG.md"
output_path = "whats_new/changelog.md"
# TODO: might need to adopt the hook that copier distributes to handle links to changelog:
#       https://github.com/copier-org/copier


def read_source() -> str:
    if docs_changelog.exists():
        return docs_changelog.read_text(encoding="utf-8")

    if base_changelog.exists():
        return base_changelog.read_text(encoding="utf-8")

    return """# Changelog

No changelog is available yet.

If you expected development changelog content here, generate `CHANGELOG_docs.md` before building the documentation.
"""


with mkdocs_gen_files.open(output_path, "w") as fd:
    fd.write(read_source())
