from __future__ import annotations

from typer.testing import CliRunner

from navil.cli.app import app

runner = CliRunner()


def test_cli_help() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Navil" in result.output
