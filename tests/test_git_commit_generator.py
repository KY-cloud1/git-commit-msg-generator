from unittest.mock import MagicMock, patch
from main import get_staged_diff, generate_commit_message


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


def test_generate_commit_message_success():
    expected_message = "feat: add feature"

    with patch("main.OpenAI") as mock_openai:
        mock_client = MagicMock()
        mock_openai.return_value = mock_client

        mock_client.chat.completions.create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content=expected_message))]
        )

        result = generate_commit_message("diff")

        assert result == expected_message


def test_generate_commit_message_sends_messages():
    with patch("main.OpenAI") as mock_openai:
        mock_client = MagicMock()
        mock_openai.return_value = mock_client

        mock_client.chat.completions.create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="msg"))]
        )

        generate_commit_message("diff")

        args, kwargs = mock_client.chat.completions.create.call_args
        assert "messages" in kwargs
        assert len(kwargs["messages"]) == 2


def test_generate_commit_message_exception():
    with patch("main.OpenAI") as mock_openai:
        mock_client = MagicMock()
        mock_openai.return_value = mock_client

        mock_client.chat.completions.create.side_effect = Exception("error")

        result = generate_commit_message("diff")

        assert result is None