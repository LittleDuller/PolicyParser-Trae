import pytest


@pytest.fixture
def read_file():
    def _read_file(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    return _read_file
