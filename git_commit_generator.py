import subprocess

import pyperclip
from openai import OpenAI


# The local LLM model filename being served by llama-server.
# This is passed to the API but largely ignored by llama.cpp,
# it just needs to match what the server expects.
MODEL_NAME = "Qwen3.5-9B-Q4_K_M.gguf"

# The base URL of the local llama-server instance.
# The OpenAI client will append /chat/completions to this.
BASE_URL = "http://127.0.0.1:8080/v1"

# Point the OpenAI client at our local llama-server instead
# of OpenAI's API.
client = OpenAI(base_url=BASE_URL, api_key="not-needed")


def get_staged_diff():
    """
    Return the current git staged diff as a string.

    Runs `git diff --staged` to get only changes that have been
    added with `git add`.
    """
    result = subprocess.run(
        ["git", "diff", "--staged", "--unified=3"],
        capture_output=True,
        text=True,
    )

    # Handle git failure explicitly
    if result.returncode != 0:
        raise RuntimeError(
            f"git diff failed with return code {result.returncode}: {result.stderr}"
        )

    diff = result.stdout
    return diff


def generate_commit_message(diff):
    """
    Send the diff to the local LLM and return a commit message.

    Uses the OpenAI-compatible API exposed by llama-server.
    The api_key is required by the client library but ignored
    by the local server — any non-empty string works.

    Returns the generated message as a string, or None on failure.
    """
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                # System message sets the persona and behavior.
                {
                    "role": "system",
                    "content": "You are an expert software engineer.",
                },
                # User message provides the task and input (the diff).
                {
                    "role": "user",
                    "content": (
                        "Write a concise git commit message based "
                        "on the following diff.\n\n"
                        "Rules:\n"
                        "- Use conventional commit style "
                        "(feat, fix, refactor, chore, etc.)\n"
                        "- Title aimed for 50 characters and must "
                        "be under 72 characters\n"
                        "- Optionally include a short body if useful.\n"
                        "- Body lines must each be under 72 characters\n\n"
                        f"Diff:\n{diff}"
                    ),
                },
            ],
            timeout=45,  # seconds
        )
        return response.choices[0].message.content

    except Exception as e:
        print(f"Error: {type(e).__name__} - {e}")
        return None


def main():
    # Get the diff of everything currently staged with `git add`.
    try:
        diff = get_staged_diff()
    except Exception as e:
        print(f"Error getting git diff: {e}")
        return

    # Nothing staged — no point sending an empty diff.
    if not diff.strip():
        print("No staged changes found.")
        return

    message = generate_commit_message(diff)

    if message is None:
        print("Failed to generate commit message.")
        return

    print("\nSuggested commit message:\n")
    print(message)

    # Copy suggested commit message to clipboard.
    try:
        pyperclip.copy(message)
        print("\nCopied to clipboard.")
    except Exception as e:
        print(f"\nFailed to copy to clipboard: {e}")


if __name__ == "__main__":
    main()