
import pytest

from unittest.mock import Mock

@pytest.fixture()
def untouchable():
    return Mock(spec=[], set_spec=[])
