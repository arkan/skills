"""Check the installed UI bundle's packaging boundaries, not model behavior."""

from pathlib import Path
import re
import unittest
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
SKILLS = (
    "ui-craft", "emil-design-eng", "animate", "review-animations", "break-ui",
    "mobile-native", "better-ui", "better-typography", "better-layout",
    "better-accessibility", "better-colors", "better-writing", "better-interface",
    "shadcn",
)


def relative_links(markdown):
    markdown = re.sub(r"^(`{3,}|~{3,}).*?^\1[^\n]*$", "", markdown, flags=re.M | re.S)
    for target in re.findall(r"!?\[[^\]]*\]\(([^\s)]+)(?:\s+[^)]*)?\)", markdown):
        url = urlsplit(target.strip("<>"))
        if not url.scheme and url.path:
            yield unquote(url.path)


class UIPackagingTests(unittest.TestCase):
    def test_selected_skills_have_unique_matching_names(self):
        for name in SKILLS:
            with self.subTest(skill=name):
                text = (ROOT / "skills" / name / "SKILL.md").read_text()
                self.assertTrue(text.startswith("---\n"))
                frontmatter = text.split("---", 2)[1]
                self.assertRegex(frontmatter, rf"(?m)^name: {re.escape(name)}$")
                self.assertRegex(frontmatter, r"(?m)^description: .+")

    def test_all_relative_document_and_asset_links_resolve(self):
        files = [ROOT / "docs/ui-skills.md", ROOT / "docs/ui-skills-evaluation.md"]
        for name in SKILLS:
            files.extend((ROOT / "skills" / name).rglob("*.md"))
        for file in files:
            for target in relative_links(file.read_text()):
                with self.subTest(file=str(file.relative_to(ROOT)), target=target):
                    self.assertTrue((file.parent / target).exists())

    def test_markdown_scanner_ignores_examples_and_external_targets(self):
        markdown = (
            "[Local](reference.md#section)\n![Asset](assets/icon.png)\n"
            "[Web](https://example.com/docs)\n[Anchor](#section)\n"
            "```md\n[Example](not-a-real-file.md)\n```\n"
        )
        self.assertEqual(list(relative_links(markdown)), ["reference.md", "assets/icon.png"])

    def test_explicit_only_review_policy_is_preserved(self):
        text = (ROOT / "skills/review-animations/SKILL.md").read_text()
        self.assertRegex(text.split("---", 2)[1], r"(?m)^disable-model-invocation: true$")
        self.assertFalse((ROOT / "skills/pick-ui-library").exists())
        self.assertFalse((ROOT / "skills/interface-review").exists())

    def test_router_is_model_invocable_and_references_are_discoverable(self):
        folder = ROOT / "skills/ui-craft"
        entrypoint = (folder / "SKILL.md").read_text()
        self.assertNotIn("disable-model-invocation: true", entrypoint.split("---", 2)[1])
        self.assertIn("allow_implicit_invocation: true", (folder / "agents/openai.yaml").read_text())
        pointed = set(relative_links(entrypoint))
        for reference in (folder / "references").glob("*.md"):
            self.assertIn(str(reference.relative_to(folder)), pointed)

    def test_snapshot_pins_and_notices_are_documented(self):
        script = (ROOT / "update.sh").read_text()
        documentation = (ROOT / "docs/ui-skills.md").read_text()
        for vendor in ("EMIL", "JAKUB", "SHADCN"):
            revision = re.search(rf'{vendor}_COMMIT="([0-9a-f]{{40}})"', script).group(1)
            self.assertIn(revision, documentation)
        for notice in ("emilkowalski-skills-LICENSE", "jakubkrehel-skills-LICENSE", "shadcn-ui-LICENSE"):
            self.assertIn("MIT", (ROOT / "licenses" / notice).read_text())


if __name__ == "__main__":
    unittest.main()
