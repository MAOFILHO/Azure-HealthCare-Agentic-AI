"""Compile infra/main.bicep with `az bicep build` and check the ARM output against issue #3."""
import json
import shutil
import subprocess
import unittest
from pathlib import Path

INFRA = Path(__file__).resolve().parent.parent / "infra"
MAIN = INFRA / "main.bicep"
FOUNDRY = INFRA / "foundry.bicep"


def build(path: Path = MAIN) -> dict:
    out = subprocess.run(
        ["az", "bicep", "build", "--file", str(path), "--stdout"],
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

    def test_module_endpoint_values_are_not_openai_v1(self):
        # main.bicep outputs are module references, so the suffix can only show in the module itself.
        o = build(FOUNDRY)["outputs"]
        for name in ("projectEndpoint", "resourceEndpoint"):
            value = json.dumps(o[name]["value"])
            self.assertIn("services.ai.azure.com", value)
            self.assertNotIn("openai/v1", value)


if __name__ == "__main__":
    unittest.main()
