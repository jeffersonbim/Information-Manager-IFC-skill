import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "verify_ifc_runtime.py"


class IfcRuntimeTests(unittest.TestCase):
    def test_runtime_smoke_script_requires_positive_negative_and_nonzero_coverage(self):
        smoke = ROOT / "scripts" / "smoke_ifc_ids_runtime.py"
        self.assertTrue(smoke.is_file())
        content = smoke.read_text(encoding="utf-8")
        self.assertIn("applicable == 2", content)
        self.assertIn("passed == 1", content)
        self.assertIn("failed == 1", content)
        self.assertIn("coverage_zero_zero", content)

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

    def test_runtime_verifier_blocks_unknown_or_mismatched_versions(self):
        module = self.load_module()
        result = module.verify_runtime(
            importer=lambda name: {
                "ifcopenshell": type("Ifc", (), {"version": "unknown"})(),
                "ifctester": type("Ids", (), {"__version__": "0.8.4"})(),
            }[name]
        )
        self.assertFalse(result["safe_to_execute"])
        self.assertIn("ifcopenshell_version_unknown", result["reason_codes"])
        self.assertIn("ifctester_version_mismatch", result["reason_codes"])

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
        batch = json.loads((ROOT / "openclaw" / "config-sandbox-ifc.batch.json").read_text(encoding="utf-8"))
        self.assertEqual(batch[0]["value"]["docker"]["image"], "openclaw-sandbox-ifc:0.8.5")

    def test_parameter_planner_is_configured_for_both_runtimes(self):
        config = json.loads((ROOT / "openclaw" / "openclaw.json.example").read_text(encoding="utf-8"))
        agent_ids = {agent["id"] for agent in config["agents"]["list"]}
        self.assertIn("ifc-parameter-planner", agent_ids)
        allowed = set(config["agents"]["list"][0]["subagents"]["allowAgents"])
        self.assertIn("ifc-parameter-planner", allowed)
        self.assertTrue((ROOT / "openclaw" / "workspaces" / "ifc-parameter-planner" / "AGENTS.md").is_file())
        self.assertTrue((ROOT / ".claude" / "agents" / "ifc-parameter-planner.md").is_file())
        mcp_contract = (ROOT / "references" / "revit-mcp-execution.md").read_text(encoding="utf-8")
        self.assertIn("request_id", mcp_contract)
        self.assertIn("SMR", mcp_contract)
        self.assertIn("Claude executor", mcp_contract)
        self.assertIn("todo o seu catálogo de ferramentas é aprovado", mcp_contract)
        self.assertIn("autorização da operação", mcp_contract)

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
        self.assertTrue((ROOT / ".claude" / "agents" / "ifc-mapping-validator.md").is_file())
        self.assertTrue((ROOT / ".claude" / "agents" / "ifc-parameter-planner.md").is_file())
        self.assertTrue((ROOT / ".claude" / "agents" / "ifc-consolidator.md").is_file())
        planner = (ROOT / "references" / "agent-parameter-planner.md").read_text(encoding="utf-8")
        for classification in (
            "NATIVO_REVIT", "NATIVO_IFC", "CONFIGURACAO_EXPORTACAO",
            "PARAMETRO_COMPARTILHADO", "PARAMETRO_PROJETO", "CALCULADO",
            "NAO_APLICAVEL", "NAO_VERIFICAVEL", "CONFLITO", "REVISAO_HUMANA",
        ):
            self.assertIn(classification, planner)
        self.assertTrue((ROOT / "scripts" / "install_claude_runtime.py").is_file())
        self.assertTrue((ROOT / "scripts" / "run_ifc_python.py").is_file())

    def test_installer_reports_missing_docker_without_traceback(self):
        installer_path = ROOT / "scripts" / "install_ifc_runtime.py"
        spec = importlib.util.spec_from_file_location("install_ifc_runtime", installer_path)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.resolve_docker(finder=lambda _: None, fallback_paths=[])
        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["reason_code"], "docker_cli_not_found")


if __name__ == "__main__":
    unittest.main()
