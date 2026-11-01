"""Issue #41: infra/budget.bicep (20 USD, 75% alert) and the deploy.sh --budget-email flag."""
import json
import re
import shutil
import subprocess
import unittest
from pathlib import Path

from tests.test_infra_scripts import DEPLOY, ScriptCase

ROOT = Path(__file__).resolve().parent.parent
BUDGET = ROOT / "infra" / "budget.bicep"
EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
# Demo address for the fake az only; it is never written to a file.
DEMO_EMAIL = "demo" + "@" + "example.invalid"


def build() -> dict:
    out = subprocess.run(
        ["az", "bicep", "build", "--file", str(BUDGET), "--stdout"],
        capture_output=True, text=True,
    )
    assert out.returncode == 0, out.stderr
    return json.loads(out.stdout)


@unittest.skipUnless(shutil.which("az"), "az CLI not installed")
class BudgetBicepTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.arm = build()
        cls.budget = next(
            r for r in cls.arm["resources"] if r["type"] == "Microsoft.Consumption/budgets"
        )["properties"]

    def test_subscription_scope(self):
        self.assertIn("subscriptionDeploymentTemplate", self.arm["$schema"])

    def test_twenty_usd_monthly_cost_budget(self):
        self.assertEqual(self.budget["category"], "Cost")
        self.assertEqual(self.budget["timeGrain"], "Monthly")
        self.assertIn("20", str(self.arm["parameters"]["amount"]["defaultValue"]))

    def test_alerts_at_75_and_100_percent_of_actual_cost(self):
        n = self.budget["notifications"].values()
        self.assertEqual(sorted(x["threshold"] for x in n), [75, 100])
        self.assertTrue(all(x["thresholdType"] == "Actual" and x["enabled"] for x in n))

    def test_email_is_required_with_no_default(self):
        self.assertNotIn("defaultValue", self.arm["parameters"]["contactEmail"])

    def test_no_email_value_in_project_files(self):
        # Project files only; the board tooling under .claude and .agents ships its own examples.
        files = [*(ROOT / "infra").iterdir(), *(ROOT / "tests").glob("*.py"),
                 *(ROOT / ".github").rglob("*.yml"), ROOT / "README.md", ROOT / "docs" / "RUNBOOK.md"]
        for path in files:
            self.assertIsNone(EMAIL.search(path.read_text(errors="ignore")), str(path))


class DeployBudgetFlagTest(ScriptCase):
    def creates(self):
        return [c for c in self.az_calls() if c.startswith("deployment sub create")]

    def test_without_flag_no_budget_deployment(self):
        self.run_script(DEPLOY)
        self.assertFalse(any("budget.bicep" in c for c in self.az_calls()))

    def test_flag_deploys_budget_with_the_email(self):
        out = self.run_script(DEPLOY, "--budget-email", DEMO_EMAIL)
        self.assertEqual(out.returncode, 0, out.stderr)
        budget = [c for c in self.creates() if "budget.bicep" in c]
        self.assertEqual(len(budget), 1)
        self.assertIn(f"contactEmail={DEMO_EMAIL}", budget[0])
        self.assertNotIn(DEMO_EMAIL, out.stdout + out.stderr)

    def test_flag_without_value_is_rejected(self):
        out = self.run_script(DEPLOY, "--budget-email")
        self.assertNotEqual(out.returncode, 0)
        self.assertEqual(self.az_calls(), [])
