"""Check infra/deploy.sh and infra/destroy.sh against issue #6.

A fake `az` on PATH records every call, so nothing touches Azure.
"""
import os
import shutil
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEPLOY = ROOT / "infra" / "deploy.sh"
DESTROY = ROOT / "infra" / "destroy.sh"

# Demo values only. The fake az prints them as the deployment outputs.
PROJECT_EP = "https://demo.services.ai.azure.com/api/projects/demo"
MODEL = "demo-chat-model"
RESOURCE_EP = "https://demo.services.ai.azure.com/"

FAKE_AZ = f"""#!/usr/bin/env bash
echo "$*" >> "$AZ_LOG"
case "$*" in
  "ad signed-in-user show"*) echo "00000000-0000-0000-0000-000000000000" ;;
  "deployment sub create"*) printf '%s\\n%s\\n%s\\n' "{PROJECT_EP}" "{MODEL}" "{RESOURCE_EP}" ;;
esac
exit 0
"""


class ScriptCase(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        bindir = self.tmp / "bin"
        bindir.mkdir()
        az = bindir / "az"
        az.write_text(FAKE_AZ)
        az.chmod(az.stat().st_mode | stat.S_IEXEC)
        self.log = self.tmp / "az.log"
        self.env_file = self.tmp / "out.env"
        self.env = {
            **os.environ,
            "PATH": f"{bindir}:{os.environ['PATH']}",
            "AZ_LOG": str(self.log),
            "ENV_FILE": str(self.env_file),
        }

    def run_script(self, script, *args, stdin=""):
        return subprocess.run(
            ["bash", str(script), *args],
            input=stdin, capture_output=True, text=True, env=self.env,
        )

    def az_calls(self):
        return self.log.read_text().splitlines() if self.log.exists() else []


class DeployTest(ScriptCase):
    def test_what_if_changes_nothing(self):
        out = self.run_script(DEPLOY, "--what-if")
        self.assertEqual(out.returncode, 0, out.stderr)
        calls = "\n".join(self.az_calls())
        self.assertIn("deployment sub what-if", calls)
        self.assertNotIn("deployment sub create", calls)
        self.assertFalse(self.env_file.exists())

    def test_deploy_writes_the_three_variables(self):
        out = self.run_script(DEPLOY)
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertIn("deployment sub create", "\n".join(self.az_calls()))
        text = self.env_file.read_text()
        self.assertIn(f"FOUNDRY_PROJECT_ENDPOINT={PROJECT_EP}", text)
        self.assertIn(f"FOUNDRY_MODEL_DEPLOYMENT_NAME={MODEL}", text)
        self.assertIn(f"FOUNDRY_RESOURCE_ENDPOINT={RESOURCE_EP}", text)

    def test_output_file_is_never_printed(self):
        out = self.run_script(DEPLOY)
        shown = out.stdout + out.stderr
        for value in (PROJECT_EP, MODEL, RESOURCE_EP):
            self.assertNotIn(value, shown)

    def test_output_file_is_private(self):
        self.run_script(DEPLOY)
        self.assertEqual(stat.S_IMODE(self.env_file.stat().st_mode), 0o600)

    def test_unknown_flag_is_rejected(self):
        out = self.run_script(DEPLOY, "--nope")
        self.assertNotEqual(out.returncode, 0)
        self.assertEqual(self.az_calls(), [])

    def test_default_output_file_is_gitignored(self):
        check = subprocess.run(
            ["git", "check-ignore", "-q", ".env.foundry"], cwd=ROOT,
        )
        self.assertEqual(check.returncode, 0)


class DestroyTest(ScriptCase):
    def deletes(self):
        return [c for c in self.az_calls() if c.startswith("group delete")]

    def test_wrong_name_deletes_nothing(self):
        out = self.run_script(DESTROY, stdin="some-other-group\n")
        self.assertNotEqual(out.returncode, 0)
        self.assertEqual(self.deletes(), [])

    def test_empty_answer_deletes_nothing(self):
        out = self.run_script(DESTROY, stdin="")
        self.assertNotEqual(out.returncode, 0)
        self.assertEqual(self.deletes(), [])

    def test_exact_name_deletes_the_group(self):
        out = self.run_script(DESTROY, stdin="K21-project-rg\n")
        self.assertEqual(out.returncode, 0, out.stderr)
        deletes = self.deletes()
        self.assertEqual(len(deletes), 1)
        self.assertIn("--name K21-project-rg", deletes[0])


class SyntaxTest(unittest.TestCase):
    def test_bash_parses(self):
        for script in (DEPLOY, DESTROY):
            r = subprocess.run(["bash", "-n", str(script)], capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)

    @unittest.skipUnless(shutil.which("shellcheck"), "shellcheck not installed")
    def test_shellcheck_passes(self):
        r = subprocess.run(
            ["shellcheck", str(DEPLOY), str(DESTROY)], capture_output=True, text=True,
        )
        self.assertEqual(r.returncode, 0, r.stdout)
