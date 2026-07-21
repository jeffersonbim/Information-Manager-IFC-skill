#!/usr/bin/env python3
"""Validate authoring-category to IFC class and PredefinedType mappings.

The pre-export mode needs a CSV exported from the authoring application. Passing
an IFC adds post-export verification through IfcOpenShell. Rules are project/IDM
inputs; this script deliberately ships without universal category assumptions.
"""

from __future__ import annotations

import argparse
import csv
import fnmatch
import json
from collections import Counter
from pathlib import Path
from typing import Any


STATUSES = {
    "CONFORME",
    "CONFORME_POR_PADRAO",
    "INCOMPLETO",
    "INCOERENTE",
    "NAO_EXPORTADO",
    "NAO_APLICAVEL",
    "NAO_VERIFICAVEL",
    "REVISAO_HUMANA",
}


def norm(value: Any) -> str:
    return str(value or "").strip()


def upper(value: Any) -> str:
    return norm(value).upper()


def load_rules(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data.get("mappings"), list):
        raise ValueError("rules must contain a mappings array")
    return data


def load_source(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {"element_id", "category", "family", "type", "export_as", "predefined_type"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"source CSV missing columns: {', '.join(sorted(missing))}")
        return [{key: norm(value) for key, value in row.items()} for row in reader]


def specificity(rule: dict[str, Any]) -> int:
    return sum(rule.get(key, "*") not in ("", "*") for key in ("category", "family_pattern", "type_pattern"))


def find_rule(row: dict[str, str], rules: list[dict[str, Any]]) -> dict[str, Any] | None:
    candidates = []
    for rule in rules:
        checks = (
            fnmatch.fnmatchcase(upper(row["category"]), upper(rule.get("category", "*"))),
            fnmatch.fnmatchcase(upper(row["family"]), upper(rule.get("family_pattern", "*"))),
            fnmatch.fnmatchcase(upper(row["type"]), upper(rule.get("type_pattern", "*"))),
        )
        if all(checks):
            candidates.append(rule)
    return max(candidates, key=specificity) if candidates else None


def allowed_map(rule: dict[str, Any]) -> dict[str, set[str]]:
    result: dict[str, set[str]] = {}
    for item in rule.get("allowed_mappings", []):
        result[upper(item.get("ifc_class"))] = {upper(value) for value in item.get("predefined_types", [])}
    return result


def load_ifc(path: Path) -> dict[str, Any]:
    try:
        import ifcopenshell  # type: ignore
        from ifcopenshell.util.element import get_type  # type: ignore
    except ImportError as exc:
        raise RuntimeError("IfcOpenShell is required when --ifc is used") from exc

    model = ifcopenshell.open(str(path))
    indexed = {}
    for entity in model.by_type("IfcRoot"):
        guid = norm(getattr(entity, "GlobalId", ""))
        if not guid:
            continue
        type_entity = get_type(entity)
        occurrence_predefined = norm(getattr(entity, "PredefinedType", ""))
        type_predefined = norm(getattr(type_entity, "PredefinedType", "")) if type_entity else ""
        effective = type_predefined if type_predefined and upper(type_predefined) != "NOTDEFINED" else occurrence_predefined
        indexed[guid] = {
            "ifc_class": entity.is_a(),
            "predefined_type": effective,
            "occurrence_predefined_type": occurrence_predefined,
            "type_predefined_type": type_predefined,
            "object_type": norm(getattr(entity, "ObjectType", "")),
        }
    return {"schema": norm(model.schema), "entities": indexed}


def finding(row: dict[str, str], status: str, rule_id: str | None, reasons: list[str], actual: dict[str, str] | None = None) -> dict[str, Any]:
    assert status in STATUSES
    return {
        "element_id": row["element_id"],
        "global_id": row.get("global_id", ""),
        "category": row["category"],
        "family": row["family"],
        "type": row["type"],
        "rule_id": rule_id,
        "status": status,
        "reasons": reasons,
        "source": {"export_as": row["export_as"], "predefined_type": row["predefined_type"]},
        "ifc": actual,
    }


def validate(rows: list[dict[str, str]], rules_doc: dict[str, Any], ifc: dict[str, Any] | None = None) -> dict[str, Any]:
    results = []
    for row in rows:
        rule = find_rule(row, rules_doc["mappings"])
        if rule is None:
            results.append(finding(row, "REVISAO_HUMANA", None, ["nenhuma regra de categoria/família/tipo aplicável"]))
            continue
        rule_id = norm(rule.get("rule_id"))
        if rule.get("not_applicable"):
            results.append(finding(row, "NAO_APLICAVEL", rule_id, ["regra marca o objeto como não aplicável ao intercâmbio"]))
            continue

        allowed = allowed_map(rule)
        explicit = bool(rule.get("requirements", {}).get("explicit_export_as", False))
        explicit_predefined = bool(rule.get("requirements", {}).get("explicit_predefined_type", False))
        source_class = upper(row["export_as"])
        source_predefined = upper(row["predefined_type"])
        reasons = []
        status = "CONFORME"

        if explicit and not source_class:
            status, reasons = "INCOMPLETO", ["mapeamento explícito obrigatório, mas export_as está vazio"]
        elif source_class and source_class not in allowed:
            status, reasons = "INCOERENTE", [f"classe de origem {row['export_as']} não permitida pela regra"]
        elif source_class and source_predefined and source_predefined not in allowed.get(source_class, set()):
            status, reasons = "INCOERENTE", [f"PredefinedType {row['predefined_type']} não permitido para {row['export_as']}"]
        elif source_class and explicit_predefined and not source_predefined:
            status, reasons = "INCOMPLETO", ["PredefinedType explícito obrigatório, mas está vazio"]
        elif not source_class:
            status, reasons = "CONFORME_POR_PADRAO", ["mapeamento explícito não é obrigatório; validar resultado exportado"]

        actual = None
        if ifc is not None:
            guid = row.get("global_id", "")
            if not guid:
                status, reasons = "NAO_VERIFICAVEL", ["GlobalId ausente; não é possível reconciliar origem e IFC"]
            else:
                actual = ifc["entities"].get(guid)
                if actual is None:
                    status, reasons = "NAO_EXPORTADO", ["GlobalId da origem não encontrado no IFC"]
                else:
                    actual_class = upper(actual["ifc_class"])
                    actual_predefined = upper(actual["predefined_type"])
                    if actual_class not in allowed:
                        status, reasons = "INCOERENTE", [f"classe IFC resultante {actual['ifc_class']} não permitida"]
                    elif actual_predefined and actual_predefined not in allowed[actual_class]:
                        status, reasons = "INCOERENTE", [f"PredefinedType efetivo {actual['predefined_type']} não permitido"]
                    elif actual_predefined == "USERDEFINED" and not actual["object_type"]:
                        status, reasons = "INCOERENTE", ["USERDEFINED exige ObjectType"]
                    elif not actual_predefined or actual_predefined == "NOTDEFINED":
                        if actual_predefined not in allowed[actual_class] and not rule.get("requirements", {}).get("allow_not_defined", False):
                            status, reasons = "INCOMPLETO", ["PredefinedType efetivo ausente ou NOTDEFINED"]
                    elif status == "CONFORME_POR_PADRAO":
                        reasons = ["mapeamento padrão permitido e resultado IFC compatível"]

        results.append(finding(row, status, rule_id, reasons, actual))

    counts = Counter(item["status"] for item in results)
    return {
        "status": "warning" if any(key not in ("CONFORME", "CONFORME_POR_PADRAO", "NAO_APLICAVEL") for key in counts) else "success",
        "mode": "pre_and_post_export" if ifc else "pre_export",
        "rules_version": rules_doc.get("version"),
        "ifc_schema": ifc.get("schema") if ifc else rules_doc.get("ifc_schema"),
        "population": len(rows),
        "summary": dict(sorted(counts.items())),
        "findings": results,
        "limitations": [] if ifc else ["sem IFC: classe e PredefinedType resultantes não foram verificados"],
        "requires_human_approval": bool(counts.get("REVISAO_HUMANA") or counts.get("INCOERENTE")),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-csv", required=True, type=Path)
    parser.add_argument("--rules", required=True, type=Path)
    parser.add_argument("--ifc", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    rules = load_rules(args.rules)
    rows = load_source(args.source_csv)
    ifc = load_ifc(args.ifc) if args.ifc else None
    result = validate(rows, rules, ifc)
    payload = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        args.output.write_text(payload + "\n", encoding="utf-8")
    else:
        print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
