"""Compile infra/main.bicep with `az bicep build` and check the ARM output against issue #3."""
import json
import shutil
import subprocess
import unittest
from pathlib import Path

MAIN = Path(__file__).resolve().parent.parent / "infra" / "main.bicep"


def build() -> dict:
    out = subprocess.run(
        ["az", "bicep", "build", "--file", str(MAIN), "--stdout"],
        capture_output=True, text=True,
    )
    assert out.returncode == 0, out.stderr
    return json.loads(out.stdout)


@unittest.skipUnless(shutil.which("az"), "az CLI not installed")
class MainBicepTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.arm = build()

    def test_builds_with_no_errors(self):
        self.assertNotIn("ERROR", json.dumps(self.arm.get("metadata", {})))

    def test_subscription_scope(self):
        self.assertIn("subscriptionDeploymentTemplate", self.arm["$schema"])

    def test_defaults_match_guide(self):
        p = self.arm["parameters"]
        self.assertEqual(p["resourceGroupName"]["defaultValue"], "K21-project-rg")
        self.assertEqual(p["foundryName"]["defaultValue"], "k21-healthcare")
        self.assertEqual(p["projectName"]["defaultValue"], "K21-healthcare")
        self.assertEqual(p["location"]["defaultValue"], "eastus2")

    def test_outputs_endpoints_without_openai_v1_suffix(self):
        o = self.arm["outputs"]
        for name in ("projectEndpoint", "resourceEndpoint"):
            self.assertIn(name, o)
            self.assertNotIn("openai/v1", json.dumps(o[name]))


if __name__ == "__main__":
    unittest.main()
