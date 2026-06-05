import pytest
import os
import json
import shutil
from pathlib import Path
from logs.logger import Logger


@pytest.fixture
def runs_dir():
    return Path(__file__).resolve().parents[2] / "runs"


@pytest.fixture(autouse=True)
def cleanup_runs(runs_dir):
    before = set(os.listdir(runs_dir)) if runs_dir.exists() else set()
    yield
    if runs_dir.exists():
        for run in os.listdir(runs_dir):
            if run not in before:
                run_path = runs_dir / run
                if run_path.is_dir():
                    shutil.rmtree(run_path)


def test_init_creates_runs_directory(runs_dir):
    Logger()
    assert runs_dir.exists()


def test_init_creates_run_directory(runs_dir):
    existing = len(os.listdir(runs_dir)) if runs_dir.exists() else 0
    logger = Logger()
    expected = runs_dir / f"run_{existing + 1:03d}"
    assert expected.exists()
    assert str(logger.run_dir) == str(expected)


def test_multiple_loggers_increment_run_number(runs_dir):
    start = len(os.listdir(runs_dir)) + 1 if runs_dir.exists() else 1
    Logger()
    Logger()
    Logger()
    assert (runs_dir / f"run_{start:03d}").exists()
    assert (runs_dir / f"run_{start + 1:03d}").exists()
    assert (runs_dir / f"run_{start + 2:03d}").exists()


def test_store_creates_messages_log():
    logger = Logger()
    logger.store({"key": "value"})
    assert os.path.exists(os.path.join(logger.run_dir, "messages_log.json"))


def test_store_writes_correct_json():
    logger = Logger()
    data = {"key": "value", "nested": {"data": [1, 2, 3]}}
    logger.store(data)
    with open(os.path.join(logger.run_dir, "messages_log.json"), "r") as f:
        saved = json.load(f)
    assert saved == data


def test_store_formats_json_with_indent():
    logger = Logger()
    logger.store({"key": "value"})
    with open(os.path.join(logger.run_dir, "messages_log.json"), "r") as f:
        content = f.read()
    assert "\n" in content