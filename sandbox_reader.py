"""Read UTF-8 files from the Developer Toolbox sandbox."""

import os
import stat
from contextlib import ExitStack
from pathlib import Path


SANDBOX = Path(__file__).resolve().with_name("sandbox")


def read_sandbox_text(path: str, root: Path = SANDBOX) -> str:
    """Read a regular file named relative to the sandbox root."""
    relative_path = Path(path)
    if relative_path.is_absolute() or not relative_path.parts or ".." in relative_path.parts:
        raise ValueError("Use a file path inside the sandbox without '..'.")

    # Open each directory relative to the previous one, without following links.
    directory_flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    with ExitStack() as stack:
        directory = os.open(root, directory_flags)
        stack.callback(os.close, directory)
        for part in relative_path.parts[:-1]:
            directory = os.open(part, directory_flags, dir_fd=directory)
            stack.callback(os.close, directory)

        file_flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK
        file_descriptor = os.open(relative_path.name, file_flags, dir_fd=directory)
        stack.callback(os.close, file_descriptor)
        if not stat.S_ISREG(os.fstat(file_descriptor).st_mode):
            raise ValueError("Choose a regular file inside the sandbox.")

        with open(file_descriptor, encoding="utf-8", closefd=False) as file:
            return file.read()
