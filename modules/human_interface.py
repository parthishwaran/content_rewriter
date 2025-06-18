import os
from pathlib import Path
from datetime import datetime
import tempfile
import subprocess

class HumanInterface:
    @staticmethod
    def get_human_input(prompt, default=None):
        """Get input from the user with an optional default value."""
        if default:
            user_input = input(f"{prompt} [{default}]: ") or default
        else:
            user_input = input(f"{prompt}: ")
        return user_input

    @staticmethod
    def edit_content_in_editor(content, editor=None):
        """
        Open content in a text editor for human editing.
        Returns the edited content or None if editing was aborted.
        """
        # Create a temporary file
        with tempfile.NamedTemporaryFile(suffix=".txt", mode='w+', delete=False) as temp_file:
            temp_file.write(content)
            temp_file_path = temp_file.name
        # Determine the editor to use
        editor = editor or os.getenv('EDITOR') or 'nano'
        try:
            # Open the editor
            subprocess.call([editor, temp_file_path])
            # Read the edited content
            with open(temp_file_path, 'r') as f:
                edited_content = f.read()
            # Clean up
            os.unlink(temp_file_path)
            return edited_content if edited_content != content else None
        except Exception as e:
            print(f"Error during editing: {e}")
            os.unlink(temp_file_path)
            return None

    @staticmethod
    def display_content_differences(original, modified, original_label="Original", modified_label="Modified"):
        """Display differences between two versions of content."""
        from difflib import unified_diff
        print(f"\n--- Differences between {original_label} and {modified_label} ---")
        diff = unified_diff(
            original.splitlines(keepends=True),
            modified.splitlines(keepends=True),
            fromfile=original_label,
            tofile=modified_label
        )
        for line in diff:
            if line.startswith('+'):
                print(f"\033[92m{line}\033[0m", end='')  # Green for additions
            elif line.startswith('-'):
                print(f"\033[91m{line}\033[0m", end='')  # Red for deletions
            elif line.startswith('@@'):
                print(f"\033[94m{line}\033[0m", end='')  # Blue for location info
            else:
                print(line, end='')
        print("\n--- End of differences ---\n")

    @staticmethod
    def get_user_choice(prompt, options):
        """Present a menu of options and get user choice."""
        print(prompt)
        for i, option in enumerate(options, 1):
            print(f"{i}. {option}")
        while True:
            try:
                choice = int(input("Enter your choice: "))
                if 1 <= choice <= len(options):
                    return choice
                print(f"Please enter a number between 1 and {len(options)}")
            except ValueError:
                print("Please enter a valid number.")
