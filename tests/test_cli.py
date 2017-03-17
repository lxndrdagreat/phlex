import pytest
from click.testing import CliRunner
from phlex import cli


@pytest.fixture
def runner():
    return CliRunner()


def test_cli(runner):
    result = runner.invoke(cli.main)
    assert result.exit_code == 0
    assert not result.exception


# def test_cli_with_option(runner):
#     result = runner.invoke(cli.main, ['--as-cowboy'])
#     assert not result.exception
#     assert result.exit_code == 0
#
#
# def test_cli_with_arg(runner):
#     result = runner.invoke(cli.main, ['Dan'])
#     assert result.exit_code == 0
#     assert not result.exception
