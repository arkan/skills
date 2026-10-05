"""Exercise UI synchronization against local, pinned Git sources."""

import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (ROOT / "update.sh").read_text()
REAL_GIT = shutil.which("git")
VENDORS = {
    "EMIL": ("emilkowalski/skills", "LICENSE", "emilkowalski-skills-LICENSE"),
    "JAKUB": ("jakubkrehel/skills", "LICENSE", "jakubkrehel-skills-LICENSE"),
    "SHADCN": ("shadcn-ui/ui", "LICENSE.md", "shadcn-ui-LICENSE"),
}


def selected_skills(vendor):
    if vendor == "SHADCN":
        return ["shadcn"]
    return re.search(rf"{vendor}_SKILLS=\(\n(.*?)\n\)", SCRIPT, re.S).group(1).split()


def snapshot(root):
    return {
        str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in root.rglob("*")
        if path.is_file() and ".git" not in path.relative_to(root).parts
    }


def git(root, *args):
    return subprocess.check_output(
        [REAL_GIT, "-C", str(root), *args], stderr=subprocess.DEVNULL, text=True
    ).strip()


def commit(root):
    git(root, "add", ".")
    git(root, "-c", "user.name=Sync Test", "-c", "user.email=sync@example.test",
        "commit", "--quiet", "-m", "Fixture state")


class UIUpdateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        temp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(temp.cleanup)
        cls.fixtures = {}
        cls.commits = {}
        for vendor, (repo, license_source, _) in VENDORS.items():
            root = Path(temp.name) / vendor
            root.mkdir()
            git(root, "init", "--quiet")
            for name in selected_skills(vendor):
                folder = root / "skills" / name
                folder.mkdir(parents=True)
                (folder / "SKILL.md").write_text(f"Upstream {name}\n")
                (folder / "reference.md").write_text("Supporting reference\n")
            (root / license_source).write_text(f"MIT license fixture for {repo}\n")
            commit(root)
            cls.fixtures[vendor] = root
            cls.commits[vendor] = git(root, "rev-parse", "HEAD")

    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.workspace = Path(temp.name) / "workspace"
        self.workspace.mkdir()
        git(self.workspace, "init", "--quiet")
        script = SCRIPT
        for vendor, revision in self.commits.items():
            script = re.sub(rf'{vendor}_COMMIT="[0-9a-f]+"',
                            f'{vendor}_COMMIT="{revision}"', script)
        (self.workspace / "update.sh").write_text(script)
        first = self.workspace / "skills/emil-design-eng"
        first.mkdir(parents=True)
        (first / "SKILL.md").write_text("Old skill\n")
        (first / "obsolete.md").write_text("Stale reference\n")
        for path in ("skills/prototype/SKILL.md", "notes/keep.md"):
            target = self.workspace / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("Unrelated user content\n")
        commit(self.workspace)

        self.log = Path(temp.name) / "git-calls.jsonl"
        wrappers = Path(temp.name) / "bin"
        wrappers.mkdir()
        wrapper = wrappers / "git"
        wrapper.write_text('''#!/usr/bin/env python3
import json
import os
from pathlib import Path
import subprocess
import sys

args = sys.argv[1:]
real_git = os.environ["SYNC_UI_REAL_GIT"]
with open(os.environ["SYNC_UI_LOG"], "a") as log:
    log.write(json.dumps(args) + "\\n")
if "fetch" in args:
    if os.environ.get("SYNC_UI_FETCH_FAIL"):
        sys.exit("Injected fetch failure")
    checkout = args[1]
    repo = subprocess.check_output(
        [real_git, "-C", checkout, "remote", "get-url", "origin"], text=True
    ).strip()
    fixtures = json.loads(os.environ["SYNC_UI_FIXTURES"])
    if repo not in fixtures:
        sys.exit("Unexpected vendor checkout in a UI-only update")
    args[-2] = fixtures[repo]
elif args[-2:] == ["rev-parse", "HEAD"] and os.environ.get("SYNC_UI_WRONG_COMMIT"):
    print("0" * 40)
    sys.exit(0)
result = subprocess.run([real_git, *args])
if result.returncode == 0 and "checkout" in args and os.environ.get("SYNC_UI_MISSING"):
    missing = Path(args[1]) / os.environ["SYNC_UI_MISSING"]
    if missing.exists():
        missing.unlink()
sys.exit(result.returncode)
''')
        wrapper.chmod(0o755)
        self.env = dict(os.environ)
        self.env.update({
            "PATH": str(wrappers) + os.pathsep + os.environ["PATH"],
            "SYNC_UI_REAL_GIT": REAL_GIT,
            "SYNC_UI_LOG": str(self.log),
            "SYNC_UI_FIXTURES": json.dumps({
                f"https://github.com/{repo}.git": self.fixtures[vendor].as_uri()
                for vendor, (repo, _, _) in VENDORS.items()
            }),
        })

    def run_update(self, *options):
        return subprocess.run(
            ["bash", str(self.workspace / "update.sh"), *options],
            cwd=self.workspace.parent, env=self.env, text=True,
            capture_output=True, timeout=30,
        )

    def assert_rejected_without_writes(self, message, *options):
        before = snapshot(self.workspace)
        result = self.run_update(*(options or ("--ui-only",)))
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn(message, result.stderr)
        self.assertEqual(snapshot(self.workspace), before)

    def import_and_commit(self):
        result = self.run_update("--ui-only")
        self.assertEqual(result.returncode, 0, result.stderr)
        commit(self.workspace)

    def test_ui_only_copies_complete_folders_licenses_and_preserves_other_content(self):
        unrelated = {p: (self.workspace / p).read_bytes()
                     for p in ("skills/prototype/SKILL.md", "notes/keep.md")}
        result = self.run_update("--ui-only")
        self.assertEqual(result.returncode, 0, result.stderr)
        for vendor, (_, license_source, license_destination) in VENDORS.items():
            for name in selected_skills(vendor):
                self.assertEqual(snapshot(self.workspace / "skills" / name),
                                 snapshot(self.fixtures[vendor] / "skills" / name))
            self.assertEqual(
                (self.workspace / "licenses" / license_destination).read_bytes(),
                (self.fixtures[vendor] / license_source).read_bytes(),
            )
        for path, content in unrelated.items():
            self.assertEqual((self.workspace / path).read_bytes(), content)
        self.assertNotIn("clone", self.log.read_text())

    def test_dry_run_creates_no_destinations_including_license_parent(self):
        before = snapshot(self.workspace)
        result = self.run_update("--ui-only", "--dry-run")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("obsolete.md", result.stdout)
        self.assertEqual(snapshot(self.workspace), before)
        self.assertFalse((self.workspace / "licenses").exists())
        self.assertFalse((self.workspace / "skills/shadcn").exists())

    def test_missing_final_skill_fails_before_any_ui_write(self):
        self.env["SYNC_UI_MISSING"] = "skills/shadcn/SKILL.md"
        self.assert_rejected_without_writes("Missing UI skill source")

    def test_missing_final_license_fails_before_any_ui_write(self):
        self.env["SYNC_UI_MISSING"] = "LICENSE.md"
        self.assert_rejected_without_writes("Missing UI license source")

    def test_pin_mismatch_fails_before_any_ui_write(self):
        self.env["SYNC_UI_WRONG_COMMIT"] = "1"
        self.assert_rejected_without_writes("does not match the pinned commit")

    def test_fetch_failure_stops_before_checkout_or_writes(self):
        self.env["SYNC_UI_FETCH_FAIL"] = "1"
        self.assert_rejected_without_writes("Injected fetch failure")
        self.assertNotIn('"checkout"', self.log.read_text())

    def test_wrong_skill_destination_type_fails_before_writes(self):
        (self.workspace / "skills/shadcn").write_text("Tracked file\n")
        commit(self.workspace)
        self.assert_rejected_without_writes("UI skill destination must be a directory")

    def test_wrong_license_destination_type_fails_before_writes(self):
        target = self.workspace / "licenses/shadcn-ui-LICENSE"
        target.mkdir(parents=True)
        (target / "keep.md").write_text("Tracked directory\n")
        commit(self.workspace)
        self.assert_rejected_without_writes("UI license destination must be a file")

    def test_invalid_scope_fails_before_checkout(self):
        self.assert_rejected_without_writes("Choose either", "--ui-only", "--matt-only")
        self.assertFalse(self.log.exists())

    def test_clean_repeated_sync_is_idempotent(self):
        self.import_and_commit()
        before = snapshot(self.workspace)
        result = self.run_update("--ui-only")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(snapshot(self.workspace), before)
        self.assertEqual(git(self.workspace, "status", "--porcelain"), "")

    def test_unstaged_vendor_edit_is_preserved(self):
        (self.workspace / "skills/emil-design-eng/SKILL.md").write_text("User edit\n")
        self.assert_rejected_without_writes("Local changes in UI destinations")

    def test_staged_vendor_edit_is_preserved(self):
        target = self.workspace / "skills/emil-design-eng/SKILL.md"
        target.write_text("Staged user edit\n")
        git(self.workspace, "add", str(target))
        index = git(self.workspace, "diff", "--cached")
        self.assert_rejected_without_writes("Local changes in UI destinations")
        self.assertEqual(git(self.workspace, "diff", "--cached"), index)

    def test_untracked_collision_is_preserved(self):
        target = self.workspace / "skills/shadcn/SKILL.md"
        target.parent.mkdir()
        target.write_text("Untracked user content\n")
        self.assert_rejected_without_writes("Local changes in UI destinations")

    def test_ignored_content_is_preserved(self):
        (self.workspace / ".gitignore").write_text("private-note.md\n")
        target = self.workspace / "skills/emil-design-eng/private-note.md"
        target.write_text("Ignored user content\n")
        self.assert_rejected_without_writes("Local changes in UI destinations")

    def test_changed_license_is_preserved(self):
        self.import_and_commit()
        (self.workspace / "licenses/shadcn-ui-LICENSE").write_text("User license edit\n")
        self.assert_rejected_without_writes("Local changes in UI destinations")

    def test_license_replacement_does_not_modify_external_hardlink(self):
        target = self.workspace / "licenses/shadcn-ui-LICENSE"
        target.parent.mkdir()
        outside = self.workspace.parent / "outside-license"
        outside.write_text("External content must remain intact\n")
        os.link(outside, target)
        commit(self.workspace)
        result = self.run_update("--ui-only")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(outside.read_text(), "External content must remain intact\n")
        self.assertEqual(target.read_bytes(),
                         (self.fixtures["SHADCN"] / "LICENSE.md").read_bytes())

    def test_dirty_dry_run_reports_conflict_without_writes(self):
        (self.workspace / "skills/emil-design-eng/keep.md").write_text("User note\n")
        before = snapshot(self.workspace)
        result = self.run_update("--ui-only", "--dry-run")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Local changes in UI destinations", result.stderr)
        self.assertEqual(snapshot(self.workspace), before)

    def test_symlinked_destination_is_rejected(self):
        outside = self.workspace.parent / "outside"
        outside.mkdir()
        (outside / "keep.md").write_text("Outside content\n")
        (self.workspace / "skills/shadcn").symlink_to(outside, target_is_directory=True)
        self.assert_rejected_without_writes("Refusing symlinked UI destination")
        self.assertEqual((outside / "keep.md").read_text(), "Outside content\n")

    def test_unrelated_dirty_files_do_not_block_update(self):
        (self.workspace / "notes/keep.md").write_text("Unrelated edit\n")
        result = self.run_update("--ui-only")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((self.workspace / "notes/keep.md").read_text(), "Unrelated edit\n")


if __name__ == "__main__":
    unittest.main()
