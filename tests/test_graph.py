import pytest

from rdf_linkchecker.checkers.requests_based import Checker
from rdf_linkchecker.graph import get_urls

VOCABULARY = "ontology.ttl"
ONTOLOGY = "examples.ttl"


def test_combined(ttl_files, data_regression):
    urls = list(sorted(get_urls(ttl_files)))
    data_regression.check({"urls": urls})
