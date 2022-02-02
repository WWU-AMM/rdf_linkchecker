from typer.testing import CliRunner

from rdf_linkchecker.__main__ import app


def test_fail(ttl_files):
    runner = CliRunner()
    result = runner.invoke(app, ttl_files)
    assert result.exit_code != 0, f"{result.output}\n{result.exception}"


def test_success(ttl_files, shared_datadir):
    runner = CliRunner()
    cfn = str(shared_datadir / "skip_missing.config")
    # cannot mix Path objects and strings in arg list
    args = ["--config-file", f"{cfn}"] + [str(t) for t in ttl_files]
    result = runner.invoke(app, args)
    assert result.exit_code == 0, f"{result.output}\n{result.exception}"


def test_success_empty(ttl_files, tmp_path):
    runner = CliRunner()
    # cannot mix Path objects and strings in arg list
    empty = tmp_path / "empty.ttl"
    empty.write_text("")
    args = [str(empty)]
    result = runner.invoke(app, args)
    assert result.exit_code == 0, f"{result.output}\n{result.exception}"


def test_help():
    runner = CliRunner()
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0, f"{result.output}\n{result.exception}"


def test_version():
    from rdf_linkchecker import version

    runner = CliRunner()
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0, f"{result.output}\n{result.exception}"
    assert version in result.output
