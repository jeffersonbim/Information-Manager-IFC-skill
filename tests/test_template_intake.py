from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from template_intake import REQUIRED_COLUMNS, intake  # noqa: E402


class TemplateIntakeTests(unittest.TestCase):
    def test_official_template_exposes_only_complete_rows_to_agents(self) -> None:
        result = intake(ROOT / "templates" / "Template_Consulta_Parametros_Revit_IFC.xlsx")

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["required_columns"], list(REQUIRED_COLUMNS))
        self.assertGreater(result["ready_count"], 0)
        self.assertEqual(result["blocked_count"], 0)
        for row in result["ready"]:
            values = row["values"]
            self.assertTrue(all(values[column] for column in REQUIRED_COLUMNS))


if __name__ == "__main__":
    unittest.main()
