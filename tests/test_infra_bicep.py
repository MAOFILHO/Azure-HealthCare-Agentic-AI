"""Compile infra/main.bicep with `az bicep build` and check the ARM output against issue #3."""
import json
import shutil
import subprocess
import unittest
from pathlib import Path

INFRA = Path(__file__).resolve().parent.parent / "infra"
MAIN = INFRA / "main.bicep"
FOUNDRY = INFRA / "foundry.bicep"
MODELS = INFRA / "models.bicep"


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
        self.assertEqual(p["foundryName"]["defaultValue"], "k21-carecompanion")
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


@unittest.skipUnless(shutil.which("az"), "az CLI not installed")
class ModelsBicepTest(unittest.TestCase):
    """Issue #4: gpt-5-mini and text-embedding-3-large deployments."""

    @classmethod
    def setUpClass(cls):
        cls.arm = build(MODELS)
        cls.main = build()

    def deployments(self):
        return [r for r in self.arm["resources"]
                if r["type"] == "Microsoft.CognitiveServices/accounts/deployments"]

    def test_two_deployments_default_to_guide_models(self):
        self.assertEqual(len(self.deployments()), 2)
        p = self.arm["parameters"]
        self.assertEqual(p["chatModel"]["defaultValue"], "gpt-5-mini")
        self.assertEqual(p["embeddingModel"]["defaultValue"], "text-embedding-3-large")

    def test_model_and_capacity_are_parameters(self):
        p = self.arm["parameters"]
        for name in ("chatModel", "chatCapacity", "embeddingModel", "embeddingCapacity"):
            self.assertIn(name, p)
            self.assertIn("defaultValue", p[name])

    def test_global_standard_sku(self):
        for d in self.deployments():
            self.assertEqual(d["sku"]["name"], "GlobalStandard")

    def test_outputs_deployment_names(self):
        for name in ("chatDeploymentName", "embeddingDeploymentName"):
            self.assertIn(name, self.arm["outputs"])
            self.assertIn(name, self.main["outputs"])

    def test_main_wires_models_module(self):
        names = [r["name"] for r in self.main["resources"] if r["type"] == "Microsoft.Resources/deployments"]
        self.assertIn("models", names)


if __name__ == "__main__":
    unittest.main()
