
import pytest


@pytest.fixture()
def no_requests(monkeypatch):
    monkeypatch.delattr("web3.ipc.")
