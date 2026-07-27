from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "gate3_artifacts.py"


class Gate3ArtifactsTests(unittest.TestCase):
    def test_generates_only_explicitly_approved_rows(self) -> None:
        payload = {"rows": [
            {"gate3_approval": "APROVADO", "requirement_code": "ARQ-001", "classification": "PARAMETRO_COMPARTILHADO", "revit_parameter": "LarguraBatente", "guid": "8a8ff0a0-38f6-4ecb-bd2b-92f2a0f23b25", "revit_datatype": "LENGTH", "revit_scope": "TYPE", "revit_categories": ["Doors"], "destination_type": "CUSTOM_PSET", "pset": "Pset_Esquadrias", "property": "LarguraBatente", "ifc_data_type": "PositiveLength", "ifc_class": "IfcDoor"},
            {"gate3_approval": "PENDENTE", "requirement_code": "ARQ-002", "classification": "PARAMETRO_COMPARTILHADO", "revit_parameter": "NaoPodeSair", "guid": "a3f03c0e-826d-4470-8555-09dfa5b5f167"},
        ]}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            mapping = root / "mapping.json"
            output = root / "output"
            mapping.write_text(json.dumps(payload), encoding="utf-8")
            result = subprocess.run([sys.executable, str(SCRIPT), str(mapping), "--output", str(output)], capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual((output / "parametros_compartilhados_gate3.txt").read_bytes()[:2], b"\xff\xfe")
            self.assertIn("LarguraBatente", (output / "user_defined_psets_gate3.txt").read_text(encoding="utf-8"))
            self.assertNotIn("NaoPodeSair", (output / "parametros_compartilhados_gate3.txt").read_bytes().decode("utf-16le"))
            self.assertTrue((output / "shared_parameters_tool_manifest_gate3.xml").exists())
            self.assertTrue((output / "model_checker_gate3.xml").exists())
            self.assertTrue((output / "bonsai_evidence_plan_gate4.json").exists())


if __name__ == "__main__":
    unittest.main()
