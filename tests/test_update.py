"""Exercise synchronization in isolated repositories with a local Git fixture."""

import hashlib
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (ROOT / "update.sh").read_text()
SOURCES = re.search(r"MATT_SKILLS=\(\n(.*?)\n\)", SCRIPT, re.S).group(1).split()
REAL_GIT = shutil.which("git")


def snapshot(root):
    return {
        str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in root.rglob("*")
        if path.is_file()
    }


class UpdateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture_temp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.fixture_temp.cleanup)
        cls.fixture = Path(cls.fixture_temp.name) / "upstream"
        cls.fixture.mkdir()
        for source in SOURCES:
            folder = cls.fixture / source
            folder.mkdir(parents=True)
            (folder / "SKILL.md").write_text(f"Upstream {folder.name}\n")
            (folder / "reference.md").write_text("Supporting reference\n")

        def git(*args):
            return subprocess.check_output(
                [REAL_GIT, "-C", str(cls.fixture), *args], stderr=subprocess.DEVNULL
            ).decode().strip()

        git("init", "--quiet")
        git("add", ".")
        git(
            "-c", "user.name=Sync Test", "-c", "user.email=sync@example.test",
            "commit", "--quiet", "-m", "Local synchronization fixture",
        )
        git("tag", "v1.3.1")
        cls.commit = git("rev-parse", "HEAD")

    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.workspace = Path(temp.name) / "workspace"
        self.workspace.mkdir()
        self.script = self.workspace / "update.sh"
        self.script.write_text(re.sub(
            r'MATT_COMMIT="[0-9a-f]+"', f'MATT_COMMIT="{self.commit}"', SCRIPT
        ))
        first = self.workspace / "skills" / Path(SOURCES[0]).name
        first.mkdir(parents=True)
        (first / "SKILL.md").write_text("Old skill\n")
        (first / "obsolete.md").write_text("Stale reference\n")
        for relative in ["skills/exa/keep.md", "tasks/todo.md"]:
            path = self.workspace / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("Unrelated user content\n")

        wrappers = Path(temp.name) / "bin"
        wrappers.mkdir()
        (wrappers / "git").write_text('''#!/usr/bin/env python3
import os
from pathlib import Path
import shutil
import subprocess
import sys

args = sys.argv[1:]
real_git = os.environ["SYNC_TEST_REAL_GIT"]
if args[0] == "clone":
    if args[-2] != "https://github.com/mattpocock/skills.git":
        sys.exit("Unexpected vendor checkout in a Matt-only update")
    subprocess.run([real_git, *args[:-2], os.environ["SYNC_TEST_FIXTURE"], args[-1]], check=True)
    missing = os.environ.get("SYNC_TEST_MISSING_SOURCE")
    if missing:
        shutil.rmtree(Path(args[-1]) / missing)
elif args[-2:] == ["rev-parse", "HEAD"] and os.environ.get("SYNC_TEST_WRONG_COMMIT"):
    print("0" * 40)
else:
    os.execv(real_git, [real_git, *args])
''')
        (wrappers / "git").chmod(0o755)
        self.env = dict(os.environ)
        self.env.update({
            "PATH": str(wrappers) + os.pathsep + os.environ["PATH"],
            "SYNC_TEST_REAL_GIT": REAL_GIT,
            "SYNC_TEST_FIXTURE": self.fixture.as_uri(),
        })

    def run_update(self, *options):
        return subprocess.run(
            ["bash", str(self.script), *options],
            cwd=self.workspace.parent,
            env=self.env,
            text=True,
            capture_output=True,
            timeout=30,
        )

    def test_matt_only_updates_complete_folders_and_preserves_other_content(self):
        unrelated = {
            relative: (self.workspace / relative).read_bytes()
            for relative in ["skills/exa/keep.md", "tasks/todo.md"]
        }
        result = self.run_update("--matt-only")
        self.assertEqual(result.returncode, 0, result.stderr)
        for source in SOURCES:
            self.assertEqual(
                snapshot(self.workspace / "skills" / Path(source).name),
                snapshot(self.fixture / source),
            )
        for relative, content in unrelated.items():
            self.assertEqual((self.workspace / relative).read_bytes(), content)

    def test_dry_run_does_not_write_or_create_destinations(self):
        before = snapshot(self.workspace)
        result = self.run_update("--matt-only", "--dry-run")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("obsolete.md", result.stdout)
        self.assertEqual(snapshot(self.workspace), before)
        self.assertFalse((self.workspace / "skills" / Path(SOURCES[-1]).name).exists())

    def test_missing_last_source_fails_before_updating_first_destination(self):
        self.env["SYNC_TEST_MISSING_SOURCE"] = SOURCES[-1]
        before = snapshot(self.workspace)
        result = self.run_update("--matt-only")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Missing Matt Pocock skill source", result.stderr)
        self.assertEqual(snapshot(self.workspace), before)

    def test_changed_tag_fails_before_updating_destinations(self):
        self.env["SYNC_TEST_WRONG_COMMIT"] = "1"
        before = snapshot(self.workspace)
        result = self.run_update("--matt-only")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("does not match the pinned commit", result.stderr)
        self.assertEqual(snapshot(self.workspace), before)

    def test_unknown_option_fails_without_updating_destinations(self):
        before = snapshot(self.workspace)
        result = self.run_update("--unknown-option")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Unknown option", result.stderr)
        self.assertEqual(snapshot(self.workspace), before)


if __name__ == "__main__":
    unittest.main()
