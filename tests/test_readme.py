"""Check README.md against issue #19."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
README = ROOT / "README.md"

# The issue's outline, in order. Section 1 is the title line.
SECTIONS = [
    "# CareCompanion",
    "## Why this is production-grade",
    "## Architecture",
    "## The problem and the solution",
    "## Results and impact",
    "## Lab pipeline",
    "## Tech stack",
    "## Prerequisites and setup",
    "## Running the project",
    "## Project structure",
    "## Running tests",
    "## Azure region and cost",
    "## Key engineering decisions",
    "## Author",
]


class ReadmeTests(unittest.TestCase):
    def setUp(self):
        self.text = README.read_text(encoding="utf-8")

    def test_sections_follow_the_outline(self):
        positions = [self.text.find(s) for s in SECTIONS]
        missing = [s for s, p in zip(SECTIONS, positions) if p == -1]
        self.assertEqual(missing, [])
        self.assertEqual(positions, sorted(positions))

    def test_every_script_it_names_exists(self):
        paths = set(re.findall(r"\b((?:src|infra)/[\w.-]+\.(?:py|sh))\b", self.text))
        self.assertTrue(paths)
        missing = [p for p in sorted(paths) if not (ROOT / p).exists()]
        self.assertEqual(missing, [])

    def test_every_lab_script_is_listed(self):
        for script in sorted((ROOT / "src").glob("lab0*.py")):
            self.assertIn(f"src/{script.name}", self.text)

    def test_names_the_test_and_deploy_commands(self):
        for cmd in ["python -m pytest", "infra/deploy.sh --what-if",
                    "infra/deploy.sh", "infra/destroy.sh", "az login"]:
            self.assertIn(cmd, self.text)

    def test_local_links_and_images_exist(self):
        targets = re.findall(r"\]\(([^)#\s]+)\)", self.text)
        local = [t for t in targets if not re.match(r"[a-z]+:", t)]
        missing = [t for t in local if not (ROOT / t).exists()]
        self.assertEqual(missing, [])
        images = re.findall(r"!\[[^\]]*\]\(([^)\s]+)\)", self.text)
        self.assertEqual([i for i in images if re.match(r"[a-z]+:", i)], [])

    def test_links_the_runbook(self):
        self.assertIn("](docs/RUNBOOK.md)", self.text)

    def test_contains_no_secrets_or_endpoints(self):
        self.assertNotRegex(self.text, r"https?://[^\s)]*\.azure\.com")
        self.assertNotRegex(self.text, r"https?://[^\s)]*\.azure\.net")
        self.assertNotRegex(self.text, r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")
        self.assertNotRegex(self.text, r"(?m)^FOUNDRY_\w+=\S+")


if __name__ == "__main__":
    unittest.main()
