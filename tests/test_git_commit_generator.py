from unittest.mock import MagicMock, patch
from git_commit_generator import get_staged_diff, generate_commit_message, main


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

    with patch("git_commit_generator.OpenAI") as mock_openai:
        mock_client = MagicMock()
        mock_openai.return_value = mock_client

        mock_client.chat.completions.create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content=expected_message))]
        )

        result = generate_commit_message("diff")

        assert result == expected_message


def test_generate_commit_message_sends_messages():
    with patch("git_commit_generator.OpenAI") as mock_openai:
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
    with patch("git_commit_generator.OpenAI") as mock_openai:
        mock_client = MagicMock()
        mock_openai.return_value = mock_client

        mock_client.chat.completions.create.side_effect = Exception("error")

        result = generate_commit_message("diff")

        assert result is None


def test_main_with_no_staged_changes():
    with patch("git_commit_generator.get_staged_diff", return_value=""):
        with patch("builtins.print") as mock_print:
            main()
            mock_print.assert_called_with("No staged changes found.")


def test_main_with_success():
    with patch("git_commit_generator.get_staged_diff", return_value="diff"):
        with patch("git_commit_generator.generate_commit_message", return_value="feat: add feature"):
            with patch("builtins.print") as mock_print:
                main()

                mock_print.assert_any_call("\nSuggested commit message:\n")
                mock_print.assert_any_call("feat: add feature")


def test_main_with_failure():
    with patch("git_commit_generator.get_staged_diff", return_value="diff"):
        with patch("git_commit_generator.generate_commit_message", return_value=None):
            with patch("builtins.print") as mock_print:
                main()

                mock_print.assert_any_call("Failed to generate commit message.")