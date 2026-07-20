import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "parameter_mappings.py"
SPEC = importlib.util.spec_from_file_location("parameter_mappings", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class ParameterMappingTests(unittest.TestCase):
    def test_parse_revit_instance_and_type(self):
        content = """*GROUP\tID\tNAME
GROUP\t3\tPset_DoorCommon
*PARAM\tGUID\tNAME\tDATATYPE\tDATACATEGORY\tGROUP\tVISIBLE\tDESCRIPTION\tUSERMODIFIABLE
PARAM\tguid-1\tPset_DoorCommon.FireRating\tTEXT\t\t3\t1\tIfcLabel\t1
"""
        with tempfile.TemporaryDirectory() as directory:
            instance = Path(directory) / "IFC Shared Parameters-RevitIFCBuiltIn_ALL.txt"
            instance.write_text(content, encoding="utf-8")
            record = list(MODULE.parse_revit_shared_parameters(instance, "instance"))[0]

        self.assertEqual(record["scope"], "instance")
        self.assertEqual(record["property_set"], "Pset_DoorCommon")
        self.assertEqual(record["property"], "FireRating")
        self.assertEqual(record["guid"], "guid-1")
        self.assertEqual(record["ifc_datatype"], "IfcLabel")

    def test_parse_user_defined_property_set(self):
        content = """PropertySet:\tCOBie_Specification\tT\tIfcElementType
\tNominalLength\tLength\tCOBie.Type.NominalLength
"""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "mapping.txt"
            path.write_text(content, encoding="utf-8")
            record = list(MODULE.parse_property_sets(path, "cobie-ifc2x3"))[0]

        self.assertEqual(record["scope"], "type")
        self.assertEqual(record["applicable_entities"], ["IfcElementType"])
        self.assertEqual(record["revit_parameter"], "COBie.Type.NominalLength")

    def test_authorized_sources_exclude_singapore(self):
        names = {item.path.name for item in MODULE.authorized_sources(Path("C:/irrelevant"))}
        self.assertNotIn("IFC-SG Property Mapping Export.txt", names)
        self.assertEqual(len(names), 4)

    def test_real_sources_and_query(self):
        root = Path(__file__).parents[1] / "references" / "parameter-mappings" / "sources"
        records = list(MODULE.load_records(root))
        results = MODULE.search_records(records, "CasingDepth", scope="instance", limit=5)

        self.assertGreater(len(records), 10_000)
        self.assertTrue(results)
        self.assertTrue(all(item["scope"] == "instance" for item in results))
        self.assertTrue(any(item["property"] == "CasingDepth" for item in results))
        self.assertFalse(any("SG" in item["source_file"] for item in records))

    def test_stats_are_json_serializable(self):
        root = Path(__file__).parents[1] / "references" / "parameter-mappings" / "sources"
        stats = MODULE.build_stats(MODULE.load_records(root))
        json.dumps(stats)
        self.assertEqual(stats["authorized_source_count"], 4)


if __name__ == "__main__":
    unittest.main()
