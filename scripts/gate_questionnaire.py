#!/usr/bin/env python3
"""List gate questions and validate a user's recorded answers."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


QUESTIONNAIRE = Path(__file__).parents[1] / "references" / "gates-questionnaire.json"


def load_questionnaire(path: Path = QUESTIONNAIRE) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def get_gate(number: int, questionnaire: dict[str, Any]) -> dict[str, Any]:
    for gate in questionnaire["gates"]:
        if gate["gate"] == number:
            return gate
    raise ValueError(f"Gate inexistente: {number}")


def validate_answers(gate: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    answers = payload.get("answers")
    if payload.get("gate") != gate["gate"] or not isinstance(answers, dict):
        return {
            "status": "BLOCKED",
            "gate": gate["gate"],
            "missing": [item["id"] for item in gate["questions"] if item["required"]],
            "reason_codes": ["invalid_response_contract"],
        }

    missing = []
    for question in gate["questions"]:
        value = answers.get(question["id"])
        if question["required"] and (not isinstance(value, str) or not value.strip()):
            missing.append(question["id"])

    return {
        "status": "READY" if not missing else "BLOCKED",
        "gate": gate["gate"],
        "missing": missing,
        "answered": len(gate["questions"]) - len(missing),
        "required": sum(1 for item in gate["questions"] if item["required"]),
        "reason_codes": [] if not missing else ["required_answers_missing"],
    }


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    subparsers = root.add_subparsers(dest="command", required=True)
    questions = subparsers.add_parser("questions")
    questions.add_argument("--gate", type=int, required=True, choices=range(1, 7))
    validate = subparsers.add_parser("validate")
    validate.add_argument("--gate", type=int, required=True, choices=range(1, 7))
    validate.add_argument("response", type=Path)
    return root


def main() -> int:
    args = parser().parse_args()
    questionnaire = load_questionnaire()
    gate = get_gate(args.gate, questionnaire)
    if args.command == "questions":
        result = gate
    else:
        payload = json.loads(args.response.read_text(encoding="utf-8"))
        result = validate_answers(gate, payload)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("status") != "BLOCKED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
