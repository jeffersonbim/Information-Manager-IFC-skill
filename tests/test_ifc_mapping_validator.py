import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "ifc_mapping_validator.py"
SPEC = importlib.util.spec_from_file_location("ifc_mapping_validator", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


RULES = {
    "version": "test-1",
    "ifc_schema": "IFC4",
    "mappings": [
        {
            "rule_id": "R-1",
            "category": "Walls",
            "family_pattern": "*",
            "type_pattern": "*",
            "allowed_mappings": [{"ifc_class": "IfcWall", "predefined_types": ["STANDARD", "USERDEFINED"]}],
            "requirements": {"explicit_export_as": True, "allow_not_defined": False},
        },
        {
            "rule_id": "R-2",
            "category": "Doors",
            "family_pattern": "*",
            "type_pattern": "*",
            "allowed_mappings": [{"ifc_class": "IfcDoor", "predefined_types": ["DOOR"]}],
            "requirements": {"explicit_export_as": False, "allow_not_defined": False},
        },
    ],
}


class MappingValidatorTests(unittest.TestCase):
    def test_pre_export_statuses(self):
        rows = [
            {"element_id": "1", "global_id": "g1", "category": "Walls", "family": "Basic", "type": "A", "export_as": "IfcWall", "predefined_type": "STANDARD"},
            {"element_id": "2", "global_id": "g2", "category": "Walls", "family": "Basic", "type": "B", "export_as": "", "predefined_type": ""},
            {"element_id": "3", "global_id": "g3", "category": "Doors", "family": "Single", "type": "C", "export_as": "", "predefined_type": ""},
            {"element_id": "4", "global_id": "g4", "category": "Furniture", "family": "Chair", "type": "D", "export_as": "IfcFurniture", "predefined_type": ""},
        ]
        result = MODULE.validate(rows, RULES)
        self.assertEqual(result["summary"]["CONFORME"], 1)
        self.assertEqual(result["summary"]["INCOMPLETO"], 1)
        self.assertEqual(result["summary"]["CONFORME_POR_PADRAO"], 1)
        self.assertEqual(result["summary"]["REVISAO_HUMANA"], 1)

    def test_csv_requires_columns(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.csv"
            path.write_text("element_id,category\n1,Walls\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                MODULE.load_source(path)

    def test_result_is_json_serializable(self):
        result = MODULE.validate([], RULES)
        json.dumps(result)


if __name__ == "__main__":
    unittest.main()
