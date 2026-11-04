"""Check infra/roles.bicep and its wiring in main.bicep against issue #5."""
import json
import shutil
import subprocess
import unittest
from pathlib import Path

INFRA = Path(__file__).resolve().parent.parent / "infra"
ROLES = INFRA / "roles.bicep"
MAIN = INFRA / "main.bicep"

# Built-in role definition ids, verified with `az role definition list`.
FOUNDRY_USER = "53ca6127-db72-4b80-b1b0-d745d6d5456d"  # shown as "Azure AI User" in older docs
COGNITIVE_SERVICES_USER = "a97b65f3-24c7-4388-baec-2e87135dc908"


def build(path: Path) -> dict:
    out = subprocess.run(
        ["az", "bicep", "build", "--file", str(path), "--stdout"],
        capture_output=True, text=True,
    )
    assert out.returncode == 0, out.stderr
    return json.loads(out.stdout)


@unittest.skipUnless(shutil.which("az"), "az CLI not installed")
class RolesBicepTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.roles = build(ROLES)
        cls.main = build(MAIN)

    def test_principal_id_is_a_parameter_without_default(self):
        p = self.roles["parameters"]["principalId"]
        self.assertEqual(p["type"], "string")
        self.assertNotIn("defaultValue", p)

    def test_assigns_both_roles(self):
        text = json.dumps(self.roles["variables"])
        self.assertIn(FOUNDRY_USER, text)
        self.assertIn(COGNITIVE_SERVICES_USER, text)

    def test_all_assignments_are_role_assignments(self):
        res = self.roles["resources"]
        res = list(res.values()) if isinstance(res, dict) else res
        types = {r["type"] for r in res}
        self.assertEqual(types, {"Microsoft.Authorization/roleAssignments"})

    def test_main_wires_roles_module_with_principal_id(self):
        self.assertIn("principalId", self.main["parameters"])
        res = self.main["resources"]
        res = list(res.values()) if isinstance(res, dict) else res
        deployments = [r for r in res if r["type"] == "Microsoft.Resources/deployments"]
        self.assertTrue(any(r["name"] == "roles" for r in deployments))

    def test_doc_comment_names_each_role_and_lab(self):
        text = ROLES.read_text()
        for role in ("Azure AI User", "Cognitive Services User"):
            self.assertIn(role, text)
        self.assertIn("lab05", text)
        self.assertIn("lab01", text)


if __name__ == "__main__":
    unittest.main()
