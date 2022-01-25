import pytest

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


def test_no_output_term(ttl_files, monkeypatch, caplog):
    monkeypatch.setitem(
        rdf_linkchecker.checkers.CONFIG_DEFAULTS,
        "reporting",
        {"level": "none", "target": "console"},
    )
    checker = Checker()
    checker.check()
    assert caplog.text == ""


def test_no_output_term(ttl_files, monkeypatch, tmp_path):
    fn = tmp_path / "empty.log"
    monkeypatch.setitem(
        rdf_linkchecker.checkers.CONFIG_DEFAULTS,
        "reporting",
        {"level": "none", "target": str(fn)},
    )
    checker = Checker()
    checker.check()
    # file should not be created at all
    with pytest.raises(FileNotFoundError):
        assert fn.read_text()


def test_success_no_out(ttl_files, monkeypatch, tmp_path):
    fn = tmp_path / "empty.log"
    monkeypatch.setitem(
        rdf_linkchecker.checkers.CONFIG_DEFAULTS,
        "reporting",
        {"level": "only-failed", "target": str(fn)},
    )
    checker = Checker()
    checker.check()
    assert fn.read_text() == ""


def test_success_no_console(ttl_files, monkeypatch, caplog):
    monkeypatch.setitem(
        rdf_linkchecker.checkers.CONFIG_DEFAULTS,
        "reporting",
        {"level": "only-failed", "target": "console"},
    )
    checker = Checker()
    checker.check()
    assert caplog.text == ""


def test_timeout(monkeypatch):
    timeout = 2
    monkeypatch.setitem(
        rdf_linkchecker.checkers.CONFIG_DEFAULTS,
        "connection",
        {"timeout": timeout, "retries": 2},
    )
    checker = Checker()
    checker.add_urls([f"http://httpstat.us/200?sleep={2000*timeout}"])
    assert not checker.check()


def test_owl_file():
    checker = Checker()
    checker.add_urls(["https://www.w3.org/2002/07/owl"])
    assert checker.check()


def test_wiley():
    # this URL fails if the brotli package isn't available for aiohttp to use
    checker = Checker()
    checker.add_urls(
        [
            "https://www.wiley.com/en-ae/An+Introduction+to+Numerical+Methods+and+Analysis,+2nd+Edition-p-9781118367599"
        ]
    )
    assert checker.check()
