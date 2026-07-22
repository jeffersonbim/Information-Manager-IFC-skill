import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "verify_ifc_runtime.py"


class IfcRuntimeTests(unittest.TestCase):
    def load_module(self):
        spec = importlib.util.spec_from_file_location("verify_ifc_runtime", SCRIPT)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_runtime_verifier_exists(self):
        self.assertTrue(SCRIPT.is_file())

    def test_runtime_verifier_reports_required_components(self):
        module = self.load_module()
        result = module.verify_runtime(
            importer=lambda name: {
                "ifcopenshell": type("Ifc", (), {"version": "0.8.5"})(),
                "ifctester": type("Ids", (), {"__version__": "0.8.5"})(),
            }[name]
        )
        self.assertEqual(result["status"], "ready")
        self.assertTrue(result["safe_to_execute"])
        self.assertEqual(result["components"]["ifcopenshell"]["version"], "0.8.5")
        self.assertTrue(result["components"]["ifctester"]["available"])

    def test_runtime_verifier_blocks_when_ifcopenshell_is_missing(self):
        module = self.load_module()

        def missing_import(name):
            raise ModuleNotFoundError(name)

        result = module.verify_runtime(importer=missing_import)
        self.assertEqual(result["status"], "blocked")
        self.assertFalse(result["safe_to_execute"])
        self.assertIn("ifcopenshell_unavailable", result["reason_codes"])

    def test_runtime_verifier_cli_always_emits_json(self):
        completed = subprocess.run(
            [sys.executable, str(SCRIPT)], capture_output=True, text=True, check=False
        )
        payload = json.loads(completed.stdout)
        self.assertIn(payload["status"], {"ready", "blocked"})
        self.assertIsInstance(payload["components"], dict)

    def test_openclaw_config_pins_ifc_image(self):
        config = json.loads((ROOT / "openclaw" / "openclaw.json.example").read_text(encoding="utf-8"))
        image = config["agents"]["defaults"]["sandbox"]["docker"]["image"]
        self.assertEqual(image, "openclaw-sandbox-ifc:0.8.5")

    def test_inventory_contract_requires_runtime_gate_and_version(self):
        content = (ROOT / "openclaw" / "workspaces" / "ifc-inventory" / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("verify_ifc_runtime.py", content)
        self.assertIn("safe_to_execute", content)
        self.assertIn("ifcopenshell_version", content)

    def test_claude_compatibility_layer_exists(self):
        self.assertTrue((ROOT / "CLAUDE.md").is_file())
        self.assertTrue((ROOT / ".claude" / "skills" / "information-manager-ifc" / "SKILL.md").is_file())
        self.assertTrue((ROOT / ".claude" / "agents" / "ifc-coordinator.md").is_file())
        self.assertTrue((ROOT / ".claude" / "agents" / "ifc-inventory.md").is_file())

    def test_installer_reports_missing_docker_without_traceback(self):
        installer_path = ROOT / "scripts" / "install_ifc_runtime.py"
        spec = importlib.util.spec_from_file_location("install_ifc_runtime", installer_path)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.resolve_docker(finder=lambda _: None)
        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["reason_code"], "docker_cli_not_found")


if __name__ == "__main__":
    unittest.main()
