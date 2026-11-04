"""Check .github/workflows/ci.yml against issue #15 (text checks, no YAML dependency)."""
import re
import unittest
from pathlib import Path

WORKFLOW = Path(__file__).resolve().parent.parent / ".github" / "workflows" / "ci.yml"


class CiWorkflowTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = WORKFLOW.read_text()

    def test_runs_on_pull_requests_to_staging(self):
        self.assertRegex(self.text, r"pull_request:\s*\n\s+branches:\s*\[\s*staging\s*\]")

    def test_runs_pytest(self):
        self.assertRegex(self.text, r"run:\s*python -m pytest\b")

    def test_builds_every_bicep_file(self):
        self.assertRegex(self.text, r"az bicep build --file \"?\$f\"?")
        self.assertIn("infra/*.bicep", self.text)

    def test_no_step_swallows_failures(self):
        self.assertNotIn("continue-on-error", self.text)
        self.assertIsNone(re.search(r"\|\|\s*true", self.text))


if __name__ == "__main__":
    unittest.main()
