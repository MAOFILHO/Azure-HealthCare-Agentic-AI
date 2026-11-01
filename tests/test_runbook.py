"""Check docs/RUNBOOK.md against issue #16."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RUNBOOK = ROOT / "docs" / "RUNBOOK.md"
README = ROOT / "README.md"

# The guide's lab order (User Guide sections 8 to 11).
LAB_SCRIPTS = [
    "lab01_chat.py",
    "lab02_create_agent.py",
    "lab02_chat.py",
    "lab03_tools.py",
    "lab04_knowledge.py",
    "lab05_extract.py",
    "lab05_structured.py",
    "lab06_care_team.py",
    "lab06_pipeline.py",
    "lab07_mcp.py",
]


class RunbookTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue(RUNBOOK.exists(), "docs/RUNBOOK.md is missing")
        self.text = RUNBOOK.read_text(encoding="utf-8")

    def test_labs_appear_in_the_guides_order(self):
        positions = [self.text.find(s) for s in LAB_SCRIPTS]
        self.assertNotIn(-1, positions, "a lab script is missing")
        self.assertEqual(positions, sorted(positions))

    def test_every_lab_script_in_src_is_covered(self):
        labs = {p.name for p in (ROOT / "src").glob("lab0[1-6]_*.py")}
        labs.add("lab07_mcp.py")
        self.assertLessEqual(labs, set(LAB_SCRIPTS))

    def test_each_lab_has_expected_output(self):
        self.assertGreaterEqual(self.text.count("Expected:"), len(LAB_SCRIPTS))

    def test_order_is_login_deploy_labs_cleanup_destroy(self):
        steps = ["az login", "infra/deploy.sh", "lab01_chat.py",
                 "lab07_cleanup.py", "infra/destroy.sh"]
        positions = [self.text.find(s) for s in steps]
        self.assertNotIn(-1, positions)
        self.assertEqual(positions, sorted(positions))

    def test_contains_no_secrets_or_endpoints(self):
        self.assertNotRegex(self.text, r"https?://[^\s)]*\.azure\.com")
        self.assertNotRegex(self.text, r"https?://[^\s)]*\.azure\.net")
        self.assertNotRegex(self.text, r"(?i)(api[_-]?key|secret|token|password)\s*[=:]\s*\S{8,}")
        self.assertNotRegex(self.text, r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")
        self.assertNotRegex(self.text, r"(?m)^FOUNDRY_\w+=\S+")

    def test_readme_links_the_runbook(self):
        self.assertIn("docs/RUNBOOK.md", README.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
