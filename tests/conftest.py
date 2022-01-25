import pytest


@pytest.fixture()
def ttl_files(shared_datadir):
    return list(shared_datadir.glob("*.ttl"))


@pytest.fixture(autouse=True)
def increase_timeout(monkeypatch):
    """Remove requests.sessions.Session.request for all tests."""
    import rdf_linkchecker

    monkeypatch.setitem(
        rdf_linkchecker.checkers.CONFIG_DEFAULTS,
        "connection",
        {"timeout": 6, "retries": 1},
    )
