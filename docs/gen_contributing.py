from pathlib import Path

import mkdocs_gen_files


repo_root = Path(__file__).resolve().parent.parent
source = repo_root / "CONTRIBUTING.md"
output_path = "whats_new/contributing.md"


with mkdocs_gen_files.open(output_path, "w") as fd:
    if source.exists():
        fd.write(source.read_text(encoding="utf-8"))
    else:
        fd.write(
            "# Contributing\n\n"
            "Contributor guide not found.\n"
        )

if source.exists():
    mkdocs_gen_files.set_edit_path(output_path, source)
