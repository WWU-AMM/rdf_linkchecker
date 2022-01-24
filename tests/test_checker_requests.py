import pytest

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
    urls = list(sorted(get_urls(ttl_files)))
    checker = Checker()
    checker.add_urls(urls)
    assert len(checker.urls) <= len(urls)
