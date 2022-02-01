import pytest

import rdf_linkchecker.checkers
from rdf_linkchecker.checkers.requests_based import Checker


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
