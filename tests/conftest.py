import pytest


@pytest.fixture()
def ttl_files(shared_datadir):
    return shared_datadir.glob("*.ttl")
