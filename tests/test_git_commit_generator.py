from unittest.mock import MagicMock, patch
from main import get_staged_diff


def test_get_staged_diff_returns_stdout():
    mock_output = "diff output"

    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(stdout=mock_output, stderr="", returncode=0)

        result = get_staged_diff()

        assert result == mock_output


def test_get_staged_diff_calls_git_correctly():
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(stdout="", stderr="", returncode=0)

        get_staged_diff()

        mock_run.assert_called_once_with(
            ["git", "diff", "--staged", "--unified=3"],
            capture_output=True,
            text=True,
        )


def test_get_staged_diff_handles_empty_output():
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(stdout="", stderr="", returncode=0)

        result = get_staged_diff()

        assert result == ""