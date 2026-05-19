import pytest

from maestrowf.abstracts.enums import StudyStatus
from maestrowf.conductor import Conductor
from maestrowf.utils import atomic_write_file


class DummyStudy:
    name = "dummy_study"

    def __init__(self, output_path):
        self.output_path = str(output_path)


class FinishingDag:
    name = "dummy_study"

    def execute_ready_steps(self):
        return StudyStatus.FINISHED

    def pickle(self, path):
        pass

    def write_status(self, path):
        pass


class FailingDag:
    name = "dummy_study"

    def execute_ready_steps(self):
        raise RuntimeError("boom")


def test_conductor_registration_creates_process_record(tmp_path):
    conductor = Conductor(DummyStudy(tmp_path))

    conductor_id = conductor.register_conductor()
    conductors = Conductor.get_conductors(tmp_path)

    assert conductor_id in conductors
    record = conductors[conductor_id]
    assert record["conductor_id"] == conductor_id
    assert record["study_name"] == "dummy_study"
    assert record["output_path"] == str(tmp_path)
    assert record["pid"]
    assert record["hostname"]
    assert record["argv"]
    assert record["conductor_argv"]
    assert record["conductor_executable"]
    assert record["conductor_command"]
    assert record["status"] == "running"
    assert record["started_at"]
    assert record["last_heartbeat_at"] == record["started_at"]
    assert record["ended_at"] is None
    record_path = tmp_path / "logs" / ".conductors" / \
        "{}.json".format(conductor_id)
    assert record_path.exists()


def test_conductor_heartbeat_updates_record(tmp_path):
    conductor = Conductor(DummyStudy(tmp_path))
    conductor_id = conductor.register_conductor()
    original = Conductor.get_conductors(tmp_path)[conductor_id]

    conductor.heartbeat_conductor("checking work")
    updated = Conductor.get_conductors(tmp_path)[conductor_id]

    assert updated["started_at"] == original["started_at"]
    assert updated["last_status_message"] == "checking work"
    assert updated["last_heartbeat_at"] >= original["last_heartbeat_at"]
    assert updated["status"] == "running"


def test_conductor_finish_marks_record_completed(tmp_path):
    conductor = Conductor(DummyStudy(tmp_path))
    conductor_id = conductor.register_conductor()

    conductor.finish_conductor(
        "completed", StudyStatus.FINISHED, "study finished")
    record = Conductor.get_conductors(tmp_path)[conductor_id]

    assert record["status"] == "completed"
    assert record["final_study_status"] == StudyStatus.FINISHED.name
    assert record["last_status_message"] == "study finished"
    assert record["ended_at"]


def test_multiple_conductor_records_can_coexist(tmp_path):
    conductor_a = Conductor(DummyStudy(tmp_path))
    conductor_b = Conductor(DummyStudy(tmp_path))

    id_a = conductor_a.register_conductor()
    id_b = conductor_b.register_conductor()
    conductors = Conductor.get_conductors(tmp_path)

    assert id_a in conductors
    assert id_b in conductors
    assert id_a != id_b


def test_atomic_write_file_replaces_complete_file(tmp_path):
    path = tmp_path / "record.json"
    atomic_write_file(path, '{\n  "old": true\n}\n')

    atomic_write_file(path, '{\n  "new": true\n}\n')

    assert path.read_text() == '{\n  "new": true\n}\n'


def test_monitor_marks_record_completed(tmp_path):
    conductor = Conductor(DummyStudy(tmp_path))
    conductor._setup = True
    conductor._pkl_path = str(tmp_path)
    conductor._exec_dag = FinishingDag()
    conductor.sleep_time = 1
    conductor_id = conductor.register_conductor()

    assert conductor.monitor_study() == StudyStatus.FINISHED
    record = Conductor.get_conductors(tmp_path)[conductor_id]
    assert record["status"] == "completed"
    assert record["final_study_status"] == StudyStatus.FINISHED.name


def test_monitor_marks_record_failed_on_exception(tmp_path):
    conductor = Conductor(DummyStudy(tmp_path))
    conductor._setup = True
    conductor._pkl_path = str(tmp_path)
    conductor._exec_dag = FailingDag()
    conductor.sleep_time = 1
    conductor_id = conductor.register_conductor()

    with pytest.raises(RuntimeError):
        conductor.monitor_study()

    record = Conductor.get_conductors(tmp_path)[conductor_id]
    assert record["status"] == "failed"
    assert record["last_status_message"] == \
        "monitoring failed with an exception"
