import subprocess


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
    diff = result.stdout

    return diff