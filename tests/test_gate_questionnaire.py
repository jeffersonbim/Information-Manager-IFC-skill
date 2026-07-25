import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "gate_questionnaire.py"
QUESTIONNAIRE = ROOT / "references" / "gates-questionnaire.json"


class GateQuestionnaireTests(unittest.TestCase):
    def load_module(self):
        spec = importlib.util.spec_from_file_location("gate_questionnaire", SCRIPT)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_six_gates_have_five_unique_required_questions(self):
        payload = json.loads(QUESTIONNAIRE.read_text(encoding="utf-8"))
        self.assertEqual([gate["gate"] for gate in payload["gates"]], list(range(1, 7)))
        ids = []
        for gate in payload["gates"]:
            self.assertEqual(len(gate["questions"]), 5)
            self.assertTrue(all(question["required"] for question in gate["questions"]))
            ids.extend(question["id"] for question in gate["questions"])
        self.assertEqual(len(ids), len(set(ids)))

    def test_missing_answer_blocks_gate(self):
        module = self.load_module()
        questionnaire = module.load_questionnaire()
        gate = module.get_gate(1, questionnaire)
        result = module.validate_answers(
            gate,
            {"gate": 1, "answers": {"G1-Q1": "Uso definido"}},
        )
        self.assertEqual(result["status"], "BLOCKED")
        self.assertIn("G1-Q2", result["missing"])

    def test_complete_answers_make_questionnaire_ready(self):
        module = self.load_module()
        questionnaire = module.load_questionnaire()
        gate = module.get_gate(6, questionnaire)
        answers = {question["id"]: "Respondido" for question in gate["questions"]}
        result = module.validate_answers(gate, {"gate": 6, "answers": answers})
        self.assertEqual(result["status"], "READY")
        self.assertEqual(result["missing"], [])


if __name__ == "__main__":
    unittest.main()
