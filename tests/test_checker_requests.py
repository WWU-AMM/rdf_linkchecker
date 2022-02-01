import rdf_linkchecker.checkers
from rdf_linkchecker.checkers.requests_based import Checker
from rdf_linkchecker.graph import get_urls

VOCABULARY = "ontology.ttl"
ONTOLOGY = "examples.ttl"


def test_init_defaults():
    checker = Checker()
    assert checker.check()


def test_init(shared_datadir):
    checker = Checker(shared_datadir / "empty.config")
    assert checker.check()


def test_fail(ttl_files):
    checker = Checker()
    # links should not resolve w/o skipping 'missing.tld'
    urls = list(get_urls(ttl_files))
    checker.add_urls(urls)
    assert not checker.check()


def test_success(ttl_files, shared_datadir):
    checker = Checker(configfile=shared_datadir / "skip_missing.config")
    urls = list(get_urls(ttl_files))
    checker.add_urls(urls)
    assert checker.check()


def test_deduplication(ttl_files):
    urls = list(get_urls(ttl_files))
    checker = Checker()
    checker.add_urls(urls)
    assert len(checker.urls) <= len(urls)


def test_timeout(monkeypatch):
    timeout = 2
    monkeypatch.setitem(
        rdf_linkchecker.checkers.CONFIG_DEFAULTS,
        "connection",
        {"timeout": timeout, "retries": 2, "sleep": 1},
    )
    checker = Checker()
    checker.add_urls([f"http://httpstat.us/200?sleep={2000*timeout}"])
    assert not checker.check()


def test_owl_file():
    checker = Checker()
    checker.add_urls(["https://www.w3.org/2002/07/owl"])
    assert checker.check()


def test_wiley(increase_timeout):
    # this url is also pretty flaky, so more timeout and retries
    # this URL fails if the brotli package isn't available for aiohttp to use
    checker = Checker()
    checker.add_urls(
        [
            "https://www.wiley.com/en-ae/An+Introduction+to+Numerical+Methods+and+Analysis,+2nd+Edition-p-9781118367599"
        ]
    )
    assert checker.check()
