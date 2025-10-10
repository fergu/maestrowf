from collections import defaultdict
import difflib
import logging
import os
from pathlib import Path
import re
import shutil
from subprocess import check_output

import pytest

from maestrowf.datastructures.core import Study
from maestrowf.datastructures.environment import Variable
from maestrowf.specification import YAMLSpecification

from maestrowf.utils import (
    create_parentdir,
    LoggerUtility,
    make_safe_path,
    parse_version
)
from packaging.version import InvalidVersion

SCHEDULERS = set(('sched_lsf', 'sched_slurm', 'sched_flux'))
SCHED_CHECKS = defaultdict(lambda: False)


def check_lsf():
    """
    Checks if there is an lsf instance to schedule to. NOT IMPLEMENTED YET.
    """
    return False


SCHED_CHECKS['sched_lsf'] = check_lsf


def check_slurm():
    """
    Checks if there is a slurm instance to schedule to. NOT IMPLEMENTED YET.
    """
    slurm_info_func = 'sinfo'
    try:
        slurm_ver_output_lines = check_output([slurm_info_func,'-V'], encoding='utf8')
    except FileNotFoundError as fnfe:
        if fnfe.filename == slurm_info_func:
            return False

        raise

    slurm_ver_parts = slurm_ver_output_lines.split('\n')[0].split()

    try:
        version = parse_version(slurm_ver_parts[1])
    except InvalidVersion:
        # This can happen when encountering LLNL's slurm wrappers for flux machines
        print(f"Error extracting SLURM version from 'sinfo' output: {slurm_ver_output_lines} does not have a version in the expected location, item 0: {slurm_ver_parts}")
        return False

    if slurm_ver_parts[0].lower() == 'slurm' and version:
        return True

    return False


SCHED_CHECKS['sched_slurm'] = check_slurm


def check_flux():
    """
    Checks if there is a flux scheduler to schedule to.

    Returns
    -------
    True if flux bindings installed and active broker found, False if not
    """
    try:
        import flux

        fhandle = flux.Flux()

    except ImportError:
        # Flux bindings not found
        return False

    except FileNotFoundError:
        # Couldn't connect to a broker
        return False

    return True


SCHED_CHECKS['sched_flux'] = check_flux


def check_for_scheduler(sched_name):
    """
    Thin wrapper for dispatching scheduler presence testing for marking
    tests to be skipped
    """
    return SCHED_CHECKS[sched_name]()


def pytest_runtest_setup(item):
    """Helper for applying automated test marking"""
    # Scheduler dependent checks
    for marker in item.iter_markers():
        if not marker.name.startswith('sched_'):
            continue

        if marker.name not in SCHEDULERS:
            pytest.skip(f"'{marker}' is not a supported scheduler")

        print(f"CHECKING IF ON SCHEDULER: {marker.name}")
        if not check_for_scheduler(marker.name):

            pytest.skip(f"not currently running tests on '{marker}' managed system")


@pytest.fixture
def samples_spec_path():
    """
    Fixture for providing maestro specifications from the samples
    directories
    """
    def load_spec(file_name):
        samples_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'samples'
        )

        for dirpath, dirnames, filenames in os.walk(samples_dir):
            for fname in filenames:
                if file_name == fname:
                    return os.path.join(dirpath, file_name)

    return load_spec


@pytest.fixture
def spec_path():
    """
    Fixture for providing maestro specifications from test data directories
    """
    def load_spec(file_name):
        dirpath = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(dirpath, "specification", "test_specs", file_name)

    return load_spec


@pytest.fixture
def status_csv_path():
    """Fixture for providing status files from test data directories"""
    def load_status_csv(file_name):
        dirpath = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(dirpath, "status", "test_status_data", file_name)

    return load_status_csv


@pytest.fixture
def data_dir():
    """Base directory for top level shared test data."""
    return Path(__file__).parent / "data"


@pytest.fixture
def variant_expected_output(data_dir):
    def _load_variant_expected_output(expected_output_name):
        return data_dir / "expected_spec_outputs" / expected_output_name

    return _load_variant_expected_output


@pytest.fixture
def variant_spec_path(data_dir):
    """Utility fixture to load yaml spec's from top level shared test data"""
    def _load_variant_spec(spec_name):
        # Not loading it here: defer to yamlspecification..
        return data_dir / "specs" / spec_name
    return _load_variant_spec


@pytest.fixture
def load_study():
    """Fixture to provide an unexecuted study object"""
    def _load_study(spec_path, output_path, dry_run=False):

        # Setup some default args to use for testing
        use_tmp_dir = True          # NOTE: likely want to let pytest control this?
        hash_ws = False
        throttle = 0
        submission_attempts = 3
        restart_limit = 1

        # Load the Specification
        spec = YAMLSpecification.load_specification(spec_path)

        environment = spec.get_study_environment()
        steps = spec.get_study_steps()

        # Set up the output directory.
        out_dir = environment.remove("OUTPUT_PATH")
        if output_path:
            # If out is specified in the args, ignore OUTPUT_PATH.
            output_path = os.path.abspath(output_path)
        else:
            if out_dir is None:
                # If we don't find OUTPUT_PATH in the environment, assume pwd.
                out_dir = os.path.abspath("./")
            else:
                # We just take the value from the environment.
                out_dir = os.path.abspath(out_dir.value)

            out_name = spec.name.replace(" ", "_")
            # NOTE: shouldn't need timestamp for testing; omitting for now
            # out_name = "{}_{}".format(
            #     spec.name.replace(" ", "_"),
            #     time.strftime("%Y%m%d-%H%M%S")
            # )
            output_path = make_safe_path(out_dir, *[out_name])
        environment.add(Variable("OUTPUT_PATH", output_path))

        # Set up file logging
        create_parentdir(os.path.join(output_path, "logs"))
        output_path = Path(output_path)
        log_path = output_path / "logs" / "{}.log".format(spec.name)
        # log_path = os.path.join(output_path, "logs", "{}.log".format(spec.name))
        # TODO: revisit this logger/name -> don't use __name__ as in maestro.py?
        LOGGER = logging.getLogger()
        LOG_UTIL = LoggerUtility(LOGGER)
        LFORMAT = "[%(asctime)s: %(levelname)s] %(message)s"
        LOG_UTIL.add_file_handler(log_path, LFORMAT, 2)  # INFO level

        # Addition of the $(SPECROOT) to the environment.
        spec_root = os.path.split(spec_path)[0]
        spec_root = Variable("SPECROOT", os.path.abspath(spec_root))
        environment.add(spec_root)

        # Don't wire up pgen for now.
        parameters = spec.get_parameters()

        # Setup the study.
        study = Study(spec.name, spec.description, studyenv=environment,
                      parameters=parameters, steps=steps, out_path=output_path)

        # Set up the study workspace and configure it for execution.
        study.setup_workspace()
        study.configure_study(
            throttle=throttle,
            submission_attempts=submission_attempts,
            restart_limit=restart_limit,
            use_tmp=use_tmp_dir,
            hash_ws=hash_ws,
            dry_run=dry_run)
        study.setup_environment()

        batch = {"type": "local"}
        if spec.batch:
            batch = spec.batch
            if "type" not in batch:
                batch["type"] = "local"

        # Copy the spec to the output directory
        shutil.copy(spec_path, study.output_path)

        # Use the Conductor's classmethod to store the study.
        # Conductor.store_study(study)
        # Conductor.store_batch(study.output_path, batch)

        return study

    return _load_study


@pytest.fixture
def text_diff():
    """
    Fixture to diff two text streams, ignoring lines that match any pattern in
    optional ignore_patterns.  Ignore patterns are a list of regexes.
    """
    def _diff(actual, expected, ignore_patterns=None):
        """
        Compare two text streams, ignoring lines matching any ignore_patterns.
        Text streams are assumed to not be split on line endings yet.

        :param actual: The actual text output (str)
        :param expected: The expected text (str)
        :param ignore_patterns: List of regex patterns to ignore/whitelist (optional)
        :raises AssertionError: If the filtered texts do not match
        """
        if ignore_patterns is None:
            ignore_patterns = []

        def line_matches(line):
            return [re.search(pattern, line) for pattern in ignore_patterns]
        
        def filter_lines(lines):
            for line in lines:
                if any(line_matches(line)):
                    continue
                yield line

        actual_lines = actual.splitlines()
        if actual_lines and actual_lines[-1].strip() == "":
            actual_lines.pop()
        expected_lines = expected.splitlines()
        if expected_lines and expected_lines[-1].strip() == "":
            expected_lines.pop()

        def annotate_ignored_lines(lines_to_annotate):
            for line in lines_to_annotate:
                if any(line_matches(line)):
                    yield f"IGNORED: {line}"
                else:
                    yield line

        actual_filtered_lines = list(filter_lines(actual_lines))

        expected_filtered_lines = list(filter_lines(expected_lines))

        if actual_filtered_lines != expected_filtered_lines:
            actual_annotated_lines = list(annotate_ignored_lines(actual_lines))

            expected_annotated_lines = list(annotate_ignored_lines(expected_lines))

            diff = list(
                difflib.unified_diff(
                    expected_annotated_lines,
                    actual_annotated_lines,
                    fromfile="expected",
                    tofile="actual",
                    lineterm=""
                )
            )

            diff = "\n".join(diff)
            raise AssertionError(f"Text streams differ (ignoring marked lines):\n{diff}")

        return True

    return _diff


@pytest.mark.sched_flux
@pytest.fixture
def flux_jobspec_check():
    import flux

    def _diff_jobspec_keys(jobid, expected, path=None):
        """
        Helper to recursively check for values in flux jobspec's.

        :param jobid: flux jobid to look up jobspec for (int or f58)
        :param expected: nested dicts of key/values to verify in jobspec (dict)
        :param path: optional initial path in jobspec dict to search under
        """
        # NOTE: may need some helpers here if needing to mess with uri to change broker
        fh = flux.Flux()

        # Get the jobspec (do we care about original?)
        # NOTE: job_kvs_lookup vs job_info_lookup?  does it matter?

        #  Default returns id, jobspec keys
        jobspec = flux.job.job_kvs_lookup(fh, flux.job.JobID(jobid), decode=True, original=False)['jobspec']

        def assert_nested_dict_subset(actual, expected, path=None):
            """Recursively assert key/values in actual/expected dictionaries"""
            if path is None:
                path = []

            for key, expected_value in expected.items():
                current_path = path + [repr(key)]
                assert key in actual, f"Missing key at {'.'.join(current_path)}"
                actual_value = actual[key]
                if isinstance(expected_value, dict):
                    assert isinstance(actual_value, dict), (
                        f"Expected dict at {'.'.join(current_path)}, "
                        f"got {type(actual_value).__name__}"
                    )
                    assert_nested_dict_subset(actual_value,
                                              expected_value,
                                              current_path)
                elif isinstance(expected_value, list):
                    assert isinstance(actual_value, list), (
                        f"Expected list at {'.'.join(current_path)}, "
                        f"got {type(actual_value).__name__}"
                    )
                    for i, item in enumerate(expected_value):
                        if item is not ...:  # Ellipsis means "skip this index"
                            assert_nested_dict_subset(actual_value[i],
                                                      item,
                                                      current_path + [str(i)])
                else:
                    assert actual_value == expected_value, (
                        f"Value mismatch at {'.'.join(current_path)}: "
                        f"expected {expected_value!r}, got {actual_value!r}"
                    )

        assert_nested_dict_subset(jobspec, expected, path=path)

    return _diff_jobspec_keys
