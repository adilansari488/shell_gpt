import os
import platform
import shlex
from enum import Enum
from tempfile import NamedTemporaryFile
from typing import Any, Callable

import typer
from click import BadParameter


class ModelOptions(str, Enum):
    GPT3 = "gpt-3.5-turbo"
    GPT4 = "gpt-4"
    GPT4_32K = "gpt-4-32k"


def get_edited_prompt() -> str:
    """
    Opens the user's default editor to let them
    input a prompt, and returns the edited text.

    :return: String prompt.
    """
    with NamedTemporaryFile(suffix=".txt", delete=False) as file:
        # Create file and store path.
        file_path = file.name
    editor = os.environ.get("EDITOR", "vim")
    # This will write text to file using $EDITOR.
    os.system(f"{editor} {file_path}")
    # Read file when editor is closed.
    with open(file_path, "r", encoding="utf-8") as file:
        output = file.read()
    os.remove(file_path)
    if not output:
        raise BadParameter("Couldn't get valid PROMPT from $EDITOR")
    return output

def save_shell_history(command: str) -> None:
    """
    Creates a file in shell_gpt directory.
    Filename is shell_history.
    This file stores commands executed by sgpt.
    """
    current_file_path = os.path.realpath(__file__)
    current_directory = os.path.dirname(current_file_path)
    relative_path = "../shell_history"
    absolute_path = os.path.join(current_directory, relative_path)
    log_path = absolute_path
    with open(log_path, "a", encoding="utf-8") as log:
        log.write(f"{command}\n")


def run_command(command: str) -> None:
    """
    Runs a command in the user's shell.
    It is aware of the current user's $SHELL.
    :param command: A shell command to run.
    """
    if platform.system() == "Windows":
        is_powershell = len(os.getenv("PSModulePath", "").split(os.pathsep)) >= 3
        full_command = (
            f'powershell.exe -Command "{command}"'
            if is_powershell
            else f'cmd.exe /c "{command}"'
        )
    else:
        shell = os.environ.get("SHELL", "/bin/sh")
        full_command = f"{shell} -c {shlex.quote(command)}"

    os.system(full_command)
    save_shell_history(command)

def option_callback(func: Callable) -> Callable:  # type: ignore
    def wrapper(cls: Any, value: str) -> None:
        if not value:
            return
        func(cls, value)
        raise typer.Exit()

    return wrapper
