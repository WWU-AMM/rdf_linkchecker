import pytest


@pytest.fixture()
def ttl_files(shared_datadir):
    return list(shared_datadir.glob("*.ttl"))
