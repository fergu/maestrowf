import os
from pathlib import Path
import re
from shutil import rmtree
from subprocess import run
# import tempfile

import pytest

from maestrowf.specification.yamlspecification import YAMLSpecification
from rich.console import Console
console = Console()

# Tag every test in this file as requiring flux
pytestmark = [pytest.mark.sched_local,
              pytest.mark.integration,]


# @pytest.mark.parametrize(
#     "spec_name, tmp_dir, expected_step_info",
#     [
#         (
#             "hello_bye_parameterized_staged.yaml",
#             "HELLO_BYE_STAGED_LOCAL",
#             (
#                 Path("stage") / "stage.sh",
#                 Path("hello_world") / "hello_world_instance_0" / "hello_world_instance_0.sh",
#                 Path("hello_world") / "hello_world_instance_1" / "hello_world_instance_1.sh",
#                 Path("hello_world") / "hello_world_instance_2" / "hello_world_instance_2.sh",
#                 Path("hello_world") / "hello_world_instance_3" / "hello_world_instance_3.sh",
#             ),
#             (
#                 (
#                     ("This workspace:", "hello_world/hello_world_instance_0"),
#                     ("stage workspace:", "stage"),
#                 ),
#                 (
#                     ("This workspace:", "hello_world/hello_world_instance_1"),
#                     ("stage workspace:", "stage"),
#                 ),
#                 (
#                     ("This workspace:", "hello_world/hello_world_instance_2"),
#                     ("stage workspace:", "stage"),
#                 ),
#                 (
#                     ("This workspace:", "hello_world/hello_world_instance_3"),
#                     ("stage workspace:", "stage"),
#                 )
#             )
#          ),
#     ]
# )

@pytest.mark.parametrize(
    "spec_name, tmp_dir, expected_step_info",
    [
        (
            "hello_bye_parameterized_staged.yaml",
            "HELLO_BYE_STAGED_LOCAL",
            [  # stage step (single workspace)
                {
                    "step_workspace": Path("stage"),
                    "scripts": [
                        {
                            "pattern": "stage.sh",
                            "path_lines": [
                                {
                                    "line_prefix": "This workspace:",
                                    "expected_rel": "stage",
                                },
                            ],
                        },
                        {
                            "pattern": "stage.*.out",
                            "path_lines": [],  # presence only
                        },
                        {
                            "pattern": "stage.*.err",
                            "path_lines": [],  # presence only
                        },
                    ],
                },
                
                # hello_world instances
                {
                    "step_workspace": Path("hello_world/hello_world_instance_0"),
                    "scripts": [
                        {
                            "pattern": "hello_world_instance_0.sh",
                            "path_lines": [
                                {
                                    "line_prefix": "This workspace:",
                                    "expected_rel": "hello_world/hello_world_instance_0",
                                },
                                {
                                    "line_prefix": "stage workspace:",
                                    "expected_rel": "stage",
                                },
                            ],
                        },
                        {
                            "pattern": "hello_world_instance_0.*.out",
                            "path_lines": [
                                {
                                    "line_prefix": "This workspace:",
                                    "expected_rel": "hello_world/hello_world_instance_0",
                                },
                            ],
                        },
                        {
                            "pattern": "hello_world_instance_0.*.err",
                            "path_lines": [],  # presence only
                        },
                    ],
                },
                {
                    "step_workspace": Path("hello_world/hello_world_instance_1"),
                    "scripts": [
                        {
                            "pattern": "hello_world_instance_1.sh",
                            "path_lines": [
                                {
                                    "line_prefix": "This workspace:",
                                    "expected_rel": "hello_world/hello_world_instance_1",
                                },
                                {
                                    "line_prefix": "stage workspace:",
                                    "expected_rel": "stage",
                                },
                            ],
                        },
                        {
                            "pattern": "hello_world_instance_1.*.out",
                            "path_lines": [
                                {
                                    "line_prefix": "This workspace:",
                                    "expected_rel": "hello_world/hello_world_instance_1",
                                },
                            ],
                        },
                        {
                            "pattern": "hello_world_instance_1.*.err",
                            "path_lines": [],
                        },
                    ],
                },
                # similarly for hello_world_instance_2, _3 ...

                # bye_world_instance_0 with your example script
                {
                    "step_workspace": Path("bye_world/bye_world_instance_0"),
                    "scripts": [
                        {
                            "pattern": "bye_world_instance_0.sh",
                            "path_lines": [
                                {
                                    "line_prefix": "This workspace:",
                                    "expected_rel": "bye_world/bye_world_instance_0",
                                },
                                {
                                    "line_prefix": "stage workspace:",
                                    "expected_rel": "stage",
                                },
                                {
                                    "line_prefix": "hello_world workspace:",
                                    "expected_rel": "hello_world/hello_world_instance_0",
                                },
                            ],
                        },
                        {
                            "pattern": "bye_world_instance_0.*.out",
                            "path_lines": [
                                {
                                    "line_prefix": "This workspace:",
                                    "expected_rel": "bye_world/bye_world_instance_0",
                                },
                            ],
                        },
                        {
                            "pattern": "bye_world_instance_0.*.err",
                            "path_lines": [],
                        },
                    ],
                },
                # add bye_world_instance_1..3 similarly
            ],
        )
    ]
)
def test_hello_world_local(samples_spec_path,
                           check_study_success,
                           spec_name,
                           tmp_dir,
                           expected_step_info,
                           # assert_path_in_file_is_relative_to,
                           relative_path_checker,
                           fs_layout_checker):
    """
    Run integration tests using the local scheduler.
    """
    spec_path = samples_spec_path(spec_name)
    # TEMP dir run tests always trigger failure when running on flux machine?
    # tmp_outdir = tempfile.mkdtemp()

    tmp_outdir = os.path.abspath(os.path.join(os.getcwd(), tmp_dir))

    # Clean up detritus from failed tests
    if os.path.exists(tmp_outdir):
        rmtree(tmp_outdir, ignore_errors=True)  # recursively delete workspace

    spec = YAMLSpecification.load_specification(spec_path)
    study_name = spec.name

    # Run in foreground to enable easier checking of successful studies
    spec_results = run(["maestro",
                        "run",
                        "-s 1",
                        "-fg",
                        "--hashws",
                        "-o",
                        tmp_outdir,
                        "--autoyes",
                        spec_path],
                       capture_output=True,
                       encoding="utf-8")

    # TODO: add new tests: file doesn't exist if above command line has errors!
    with open(os.path.join(tmp_dir, 'logs', study_name + '_fg.log'), 'w') as testlog:
        testlog.write(spec_results.stdout)
        testlog.write(spec_results.stderr)

    completed_successfully = check_study_success(
        spec_results.stderr.split('\n'),
        study_name
    )

    console.rule("stdout")
    console.print(spec_results.stdout)
    console.rule("stderr")
    console.print(spec_results.stderr)

    """
    Demonstrates how to display a tree of files / directories with the Tree renderable.
    """

    # import os
    import pathlib
    # import sys

    # from rich import print
    from rich.filesize import decimal
    from rich.markup import escape
    from rich.text import Text
    from rich.tree import Tree


    def walk_directory(directory: pathlib.Path, tree: Tree) -> None:
        """Recursively build a Tree with directory contents."""
        # Sort dirs first then by filename
        paths = sorted(
            pathlib.Path(directory).iterdir(),
            key=lambda path: (path.is_file(), path.name.lower()),
        )
        for path in paths:
            # Remove hidden files
            if path.name.startswith("."):
                continue
            if path.is_dir():
                style = "dim" if path.name.startswith("__") else ""
                branch = tree.add(
                    f"[bold magenta]:open_file_folder: [link file://{path}]{escape(path.name)}",
                    style=style,
                    guide_style=style,
                )
                walk_directory(path, branch)
            else:
                text_filename = Text(path.name, "green")
                text_filename.highlight_regex(r"\..*$", "bold red")
                text_filename.stylize(f"link file://{path}")
                file_size = path.stat().st_size
                text_filename.append(f" ({decimal(file_size)})", "blue")
                icon = "🐍 " if path.suffix == ".py" else "📄 "
                tree.add(Text(icon) + text_filename)

    directory = tmp_outdir
    tree = Tree(
        f":open_file_folder: [link file://{directory}]{directory}",
        guide_style="bold bright_blue",
    )
    walk_directory(pathlib.Path(directory), tree)
    console.print(tree)

    # console.print(spec_results.stderr)
    assert completed_successfully
    assert spec_results.returncode == 0

    # Check expected work spaces, scripts, and script contents
    for expected_step_instance in expected_step_info:
        expected_workspace: Path = directory / expected_step_instance['step_workspace']
        expected_workspace_root: Path = expected_workspace.parent
        console.print(f"Checking for '{expected_workspace}': {expected_workspace.exists()}")
        assert expected_workspace.exists()

        for script_spec in expected_step_instance['scripts']:
            # Gen script matches
            gs_matches = fs_layout_checker.expect_file_pattern(
                directory,
                expected_step_instance['step_workspace'],
                script_spec["pattern"]
            )

            assert gs_matches, f"No files matching {script_spec['pattern']!r} in {expected_workspace}"
            for gen_script_file in gs_matches:
                for line_spec in script_spec["path_lines"]:
                    line_prefix = line_spec["line_prefix"]
                    expected_rel_path = Path(line_spec["expected_rel"])

                    rel_path = relative_path_checker(
                        gen_script_file,
                        workspace_root=Path(directory),
                        line_prefix=line_prefix,
                        # TODO: put this pattern in the input data to sync with specs?
                        path_pattern=rf'{re.escape(line_prefix)}\s+(?P<path>[^"\s]+)"?'
                    )
                    console.print(f"{rel_path=}, type: {type(rel_path)}.  {expected_rel_path=}, type: {type(expected_rel_path)}")
                    assert rel_path == expected_rel_path, (
                        f"In {gen_script_file}, for prefix {line_prefix!r}, "
                        f"expected relative path {expected_rel_path}, got {rel_path}"
                    )

    # Dummy test to force failure and show outputs
    # assert completed_successfully == 'NOT A REAL STATUS'

    # Cleanup if successful
    if os.path.exists(tmp_outdir):
        rmtree(tmp_outdir, ignore_errors=True)  # recursively delete workspace
