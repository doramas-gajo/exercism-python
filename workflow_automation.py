"""
Exercism Python Track Workflow Automation Script

This script automates the workflow for solving Exercism exercises.
It fetches the next recommended exercise, creates a git branch, downloads the
exercise, waits for the user to solve it, runs pytest, submits it
via the Exercism CLI, updates the README.md with progress badges/links,
and merges the branch back to main.
"""

import os
import sys
import requests
import subprocess
import webbrowser
from pathlib import Path
from dotenv import load_dotenv
from colorama import init as init_colorama, Fore


load_dotenv()


BASE_URL = f"https://exercism.org/api/v2"
EXERCISM_TRACK = os.environ.get("EXERCISM_TRACK")
GITHUB_USERNAME = os.environ.get("GITHUB_USERNAME")


def tests_pass(directory: Path):
        """Run the exercise tests."""
        print("Running tests...")
        command = ["python", "-m", "pytest", "-v"]
        return bool(not subprocess.run(command, cwd=directory.absolute()).returncode)


def build_auth_headers() -> dict:
    """Load token and return the authorization headers."""

    token = os.environ.get("EXERCISM_TOKEN")
    if not token:
        raise ValueError(
            "Exercism token not found.\n" \
            "Please ensure it is set in your .env file."
            )
    return {"Authorization": f"Bearer {token}"}


def fetch_track_exercises(track: str, headers: dict) -> dict:
    """Fetch all exercises for the specified track."""
    print(f"Fetching all {track} track exercises...")
    url = f"{BASE_URL}/tracks/{track}/exercises"
    return requests.get(url, headers=headers).json().get("exercises")


def fetch_track_solutions(track: str, headers: dict) -> dict:
    """Fetch all completed solutions for the specified track."""
    print(f"Fetching all {track} track solutions...")
    url = f"{BASE_URL}/solutions"
    all_solutions = requests.get(url, headers=headers).json().get("results")
    return [
        solution for solution in all_solutions
        if solution.get("track", {}).get("slug", "") == track
        and solution.get("completed_at") is not None
    ]


def update_exercise_readme(filepath: Path):
    """Remove the 'HELP.md' mention from an exercise README file."""
    print("Updating exercise README.md file...")
    with open(filepath, 'r+', encoding='utf-8') as file:
        lines = file.readlines()
        mention_line = None
        for line in lines:
            if "HELP.md" in line:
                mention_line = line
                break
        if mention_line:
            lines.remove(mention_line)
            file.seek(0)
            file.writelines(lines)
            file.truncate()


def update_repository_readme(
        solution_filepath: Path,
        completed_exercises: int,
        total_exercises: int,
        exercise_title: str,
):
    """Update the badges and list the solution in README.md file."""
    print("Updating README.md file...")
    percentage = round(((completed_exercises) / total_exercises) * 100, 1)
    track_completion_badge = \
        f"[track_completion_badge]: https://img.shields.io/badge/Track%20completion-{percentage}%25-604fcd?logo=exercism&logoColor=604fcd&labelColor=e9ecef\n"
    exercises_completed_badge = \
        f"[exercises_completed_badge]: https://img.shields.io/badge/Exercises%20completed-{completed_exercises}%2F{total_exercises}-604fcd?logo=exercism&logoColor=604fcd&labelColor=e9ecef\n"
    solution_line = \
        f"{completed_exercises}. [\"**{exercise_title}**\" solution]({solution_filepath.as_posix()}).\n"
    with open("README.md", 'r+', encoding='utf-8') as file:
        lines = file.readlines()
        new_lines = []
        for line in lines:
            if line.startswith("[track_completion_badge]"):
                new_lines.append(track_completion_badge)
                continue
            if line.startswith("[exercises_completed_badge]"):
                new_lines.append(exercises_completed_badge)
                continue
            if line == "<!-- Put next solution item here! -->\n":
                new_lines.append(solution_line)
            new_lines.append(line)
        file.seek(0)
        file.writelines(new_lines)
        file.truncate()


def main():
    """Main workflow execution."""
    init_colorama(autoreset=True)

    # Fetch data from Exercism
    headers = build_auth_headers()
    exercises = fetch_track_exercises(track=EXERCISM_TRACK, headers=headers)
    solutions = fetch_track_solutions(track=EXERCISM_TRACK, headers=headers)

    print("Processing data...")
    exercise = \
        next((ex for ex in exercises if ex.get("is_recommended")), None)
    if not exercise:
        print(Fore.GREEN + "There are no more recommended exercises.")
        sys.exit(0)
    total_exercises = len(exercises)
    completed_exercises = len(solutions)
    exercise_slug = exercise.get("slug")
    exercise_title = exercise.get("title")
    exercise_folder = Path(f"{EXERCISM_TRACK}/{exercise_slug}")

    print("Preparing repository...")
    if subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True,
        check=True
    ).stdout.strip():
        print(Fore.RED + "Git repository is dirty.")
        sys.exit(1)
    branch_name = f"exercises/{exercise_slug}"
    subprocess.run(["git", "switch", "-c", branch_name], check=True)

    # Download the exercise
    command = ["exercism", "download", "--track", EXERCISM_TRACK, "--exercise", exercise_slug]
    subprocess.run(command, check=True)
    exercise_filename = next(
        file.name for file in exercise_folder.rglob("*_test.py")
    ).replace("_test", "")

    # Wait for user solution
    solution_filepath = Path(f"{EXERCISM_TRACK}/{exercise_slug}/{exercise_filename}")
    print(f"Paused until you solve the exercise in '{solution_filepath}'.\n")
    input("Press ENTER to continue.")

    while not tests_pass(directory=exercise_folder):
        input(Fore.YELLOW + "Tests are not passing. Fix your errors and press Enter to check again...")

    print("Submitting solution to Exercism...")
    subprocess.run(["exercism", "submit", solution_filepath], check=True)
    completed_exercises += 1
    webbrowser.open(f"https://exercism.org/tracks/{EXERCISM_TRACK}/exercises/{exercise_slug}")

    # Update README.md files
    update_exercise_readme(Path(f"{exercise_folder}/README.md"))
    update_repository_readme(
        solution_filepath=solution_filepath,
        completed_exercises=completed_exercises,
        total_exercises=total_exercises,
        exercise_title=exercise_title
    )

    # Git operations
    print("Finishing the process...")
    subprocess.run(["git", "add", f"{EXERCISM_TRACK}/{exercise_slug}", "README.md"], check=True)
    message = f"Solve \"{exercise_title}\" exercise"
    subprocess.run(["git", "commit", "-m", message], check=True)
    subprocess.run(["git", "push", "-u", "origin", branch_name], check=True)
    webbrowser.open(f"https://github.com/{USER_NAME}/exercism-{EXERCISM_TRACK}/pull/new/{branch_name}")
    subprocess.run(["git", "switch", "main"], check=True)
    subprocess.run(["git", "branch", "-D", branch_name], check=True)

    print(Fore.GREEN + "Process complete!")
    print("Do not forget to mark the exercise as completed/published in the Exercism web.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nScript terminated by user.")
        sys.exit(0)
    except Exception as e:
        sys.exit(1)
