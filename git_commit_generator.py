import subprocess
from openai import OpenAI


# The local LLM model filename being served by llama-server.
# This is passed to the API but largely ignored by llama.cpp,
# it just needs to match what the server expects.
MODEL_NAME = "Qwen3.5-9B-Q4_K_M.gguf"

# The base URL of the local llama-server instance.
# The OpenAI client will append /chat/completions to this.
BASE_URL = "http://127.0.0.1:8080/v1"


def get_staged_diff():
    result = subprocess.run(
        ["git", "diff", "--staged", "--unified=3"],
        capture_output=True,
        text=True,
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
    client = OpenAI(base_url=BASE_URL, api_key="not-needed")

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert software engineer.",
                },
                {
                    "role": "user",
                    "content": (
                        "Write a concise git commit message based on the following diff.\n\n"
                        f"Diff:\n{diff}"
                    ),
                },
            ],
            timeout=45,
        )
        return response.choices[0].message.content

    except Exception as e:
        print(f"Error: {type(e).__name__} - {e}")
        return None