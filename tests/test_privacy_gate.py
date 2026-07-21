import io
import tempfile
import unittest
import zipfile
from pathlib import Path

from scripts.privacy_gate import CHUNK_SIZE, scan_file, scan_stream
from scripts.privacy_ingest import ingest


class PrivacyGateTests(unittest.TestCase):
    def test_clean_ifc_is_allowed(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "model.ifc"
            path.write_bytes(b"ISO-10303-21;\n#1=IFCWALL('abc');\nEND-ISO-10303-21;")
            result = scan_file(path)
        self.assertEqual("ALLOW", result["decision"])
        self.assertTrue(result["safe_to_forward"])
        self.assertNotIn("model.ifc", str(result))

    def test_values_are_never_returned(self):
        secret = b"pessoa@example.com"
        findings = scan_stream(io.BytesIO(b"Contato: " + secret))
        self.assertEqual(1, findings["email"])
        self.assertNotIn(secret.decode(), str(findings))

    def test_ifc_person_is_blocked_without_echoing_content(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "people.ifc"
            path.write_bytes(b"ISO-10303-21;\n#7=IFCPERSON('ID','Silva','Ana',$,$,$,$,$);")
            result = scan_file(path)
        self.assertEqual("BLOCK", result["decision"])
        self.assertIn("ifc_person_entity", result["reason_codes"])
        self.assertNotIn("Silva", str(result))
        self.assertNotIn("Ana", str(result))

    def test_valid_cpf_is_blocked(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "input.csv"
            path.write_bytes(b"cpf\n529.982.247-25\n")
            result = scan_file(path)
        self.assertEqual("BLOCK", result["decision"])
        self.assertIn("cpf", result["reason_codes"])
        self.assertNotIn("529", str(result))

    def test_ooxml_author_metadata_is_blocked(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "document.docx"
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr("docProps/core.xml", "<dc:creator>Maria</dc:creator>")
            result = scan_file(path)
        self.assertEqual("BLOCK", result["decision"])
        self.assertIn("ooxml_creator_metadata", result["reason_codes"])
        self.assertNotIn("Maria", str(result))

    def test_ooxml_embedded_payload_requires_review(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "document.docx"
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr("word/document.xml", "<document/>")
                archive.writestr("word/embeddings/payload.bin", b"opaque payload")
            result = scan_file(path)
        self.assertEqual("REVIEW", result["decision"])
        self.assertIn("ooxml_uninspected_payload", result["reason_codes"])

    def test_opaque_pdf_requires_human_review(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "document.pdf"
            path.write_bytes(b"%PDF-1.7 clean-looking bytes")
            result = scan_file(path)
        self.assertEqual("REVIEW", result["decision"])
        self.assertFalse(result["safe_to_forward"])

    def test_utf16_email_is_blocked_without_value_leak(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "input.xml"
            path.write_text("<email>segredo@example.com</email>", encoding="utf-16")
            result = scan_file(path)
        self.assertEqual("BLOCK", result["decision"])
        self.assertIn("email", result["reason_codes"])
        self.assertNotIn("segredo", str(result))

    def test_binary_disguised_as_ifc_requires_review(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "input.ifc"
            path.write_bytes(b"\x00\x01\x02binary")
            result = scan_file(path)
        self.assertEqual("REVIEW", result["decision"])

    def test_binary_after_first_4096_bytes_requires_review(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "input.ifc"
            path.write_bytes(b"ISO-10303-21;\n" + b"x" * 5000 + b"\x00hidden")
            result = scan_file(path)
        self.assertEqual("REVIEW", result["decision"])

    def test_invalid_utf8_disguised_as_ifc_requires_review(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "input.ifc"
            path.write_bytes(b"ISO-10303-21;\n" + b"\xff\xfe")
            result = scan_file(path)
        self.assertEqual("REVIEW", result["decision"])

    def test_invalid_step_signature_requires_review(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "input.ifc"
            path.write_text("not an IFC", encoding="utf-8")
            result = scan_file(path)
        self.assertEqual("REVIEW", result["decision"])

    def test_path_outside_root_is_blocked(self):
        with tempfile.TemporaryDirectory() as folder, tempfile.TemporaryDirectory() as other:
            path = Path(other) / "input.ifc"
            path.write_text("ISO-10303-21;", encoding="ascii")
            result = scan_file(path, Path(folder))
        self.assertEqual("BLOCK", result["decision"])
        self.assertIn("unsafe_input_path", result["reason_codes"])

    def test_match_crossing_chunk_boundary_is_found(self):
        prefix = b"x" * (CHUNK_SIZE - 9) + b" "
        findings = scan_stream(io.BytesIO(prefix + b"pessoa@example.com"))
        self.assertEqual(1, findings["email"])

    def test_ingest_returns_only_opaque_agent_path(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / "Nome da Pessoa.ifc"
            source.write_text("ISO-10303-21;\n#1=IFCWALL('abc');", encoding="ascii")
            result = ingest(source, root / "cleared")
            artifact = root / "cleared" / Path(str(result["agent_path"])).name
        self.assertEqual("ALLOW", result["decision"])
        self.assertNotIn("Nome", str(result))
        self.assertTrue(artifact.name.startswith(str(result["sha256"])))


if __name__ == "__main__":
    unittest.main()
