import tempfile
import unittest
from pathlib import Path

from sandbox_reader import read_sandbox_text


class SandboxReaderTests(unittest.TestCase):
    def setUp(self):
        temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(temporary_directory.cleanup)
        self.workspace = Path(temporary_directory.name)
        self.sandbox = self.workspace / "sandbox"
        self.sandbox.mkdir()
        self.outside_file = self.workspace / "outside.txt"
        self.outside_file.write_text("Outside the sandbox\n", encoding="utf-8")

    def test_reads_a_file_in_a_subfolder(self):
        folder = self.sandbox / "examples"
        folder.mkdir()
        (folder / "notes.txt").write_text("One\nTwo\n", encoding="utf-8")

        self.assertEqual(read_sandbox_text("examples/notes.txt", self.sandbox), "One\nTwo\n")

    def test_rejects_paths_outside_the_sandbox(self):
        for path in ("../outside.txt", str(self.outside_file)):
            with self.subTest(path=path), self.assertRaises(ValueError):
                read_sandbox_text(path, self.sandbox)

    def test_rejects_links_to_files_and_directories(self):
        (self.sandbox / "file-link").symlink_to(self.outside_file)
        (self.sandbox / "folder-link").symlink_to(self.workspace, target_is_directory=True)

        for path in ("file-link", "folder-link/outside.txt"):
            with self.subTest(path=path), self.assertRaises(OSError):
                read_sandbox_text(path, self.sandbox)
