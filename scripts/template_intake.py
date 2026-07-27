#!/usr/bin/env python3
"""Read the BIM requirement template without Excel dependencies.

The script is deliberately limited to intake: it validates the required input
columns and returns normalized rows. Mapping decisions remain with the governed
agents and deterministic mapping parser.
"""

from __future__ import annotations

import argparse
import json
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


REQUIRED_COLUMNS = (
    "Codigo_Requisito",
    "Descricao",
    "Disciplina",
    "Categoria_Revit",
    "Schema_IFC",
)
NS = {"x": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
REL_NS = {"r": "http://schemas.openxmlformats.org/package/2006/relationships"}


def text(node: ET.Element | None) -> str:
    return "" if node is None or node.text is None else node.text.strip()


def shared_strings(archive: zipfile.ZipFile) -> list[str]:
    try:
        root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
    except KeyError:
        return []
    return ["".join(item.itertext()) for item in root.findall("x:si", NS)]


def cell_value(cell: ET.Element, strings: list[str]) -> str:
    kind = cell.get("t")
    value = text(cell.find("x:v", NS))
    if kind == "s" and value.isdigit():
        return strings[int(value)] if int(value) < len(strings) else ""
    if kind == "inlineStr":
        return "".join(cell.find("x:is", NS).itertext()) if cell.find("x:is", NS) is not None else ""
    return value


def column_index(reference: str) -> int:
    letters = "".join(character for character in reference if character.isalpha()).upper()
    value = 0
    for character in letters:
        value = value * 26 + ord(character) - 64
    return value - 1


def worksheet_path(archive: zipfile.ZipFile, sheet_name: str) -> str:
    workbook = ET.fromstring(archive.read("xl/workbook.xml"))
    relationship_id = None
    for sheet in workbook.findall("x:sheets/x:sheet", NS):
        if sheet.get("name") == sheet_name:
            relationship_id = sheet.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id")
            break
    if relationship_id is None:
        raise ValueError(f"Aba obrigatória ausente: {sheet_name}.")
    rels = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
    for relation in rels.findall("r:Relationship", REL_NS):
        if relation.get("Id") == relationship_id:
            return "xl/" + relation.get("Target", "").lstrip("/")
    raise ValueError(f"Não foi possível localizar a aba: {sheet_name}.")


def read_rows(path: Path) -> list[list[str]]:
    with zipfile.ZipFile(path) as archive:
        strings = shared_strings(archive)
        root = ET.fromstring(archive.read(worksheet_path(archive, "Entrada_Requisitos")))
        rows: list[list[str]] = []
        for row in root.findall("x:sheetData/x:row", NS):
            values: list[str] = []
            for cell in row.findall("x:c", NS):
                index = column_index(cell.get("r", "A1"))
                while len(values) <= index:
                    values.append("")
                values[index] = cell_value(cell, strings).strip()
            rows.append(values)
        return rows


def intake(path: Path) -> dict[str, object]:
    rows = read_rows(path)
    header_row = next((index for index, row in enumerate(rows) if "Codigo_Requisito" in row), None)
    if header_row is None:
        raise ValueError("Cabeçalho Codigo_Requisito não encontrado em Entrada_Requisitos.")
    headers = rows[header_row]
    missing = [column for column in REQUIRED_COLUMNS if column not in headers]
    if missing:
        raise ValueError("Colunas obrigatórias ausentes: " + ", ".join(missing) + ".")
    result: dict[str, list[dict[str, object]]] = {"ready": [], "blocked": []}
    for source_row, row in enumerate(rows[header_row + 1 :], start=header_row + 2):
        values = {header: (row[index] if index < len(row) else "") for index, header in enumerate(headers) if header}
        if not any(values.values()):
            continue
        missing_values = [column for column in REQUIRED_COLUMNS if not values.get(column)]
        record = {"row_number": source_row, "values": values}
        if missing_values:
            result["blocked"].append({**record, "missing_required_fields": missing_values})
        else:
            result["ready"].append(record)
    return {
        "status": "success",
        "template": path.name,
        "required_columns": list(REQUIRED_COLUMNS),
        "ready_count": len(result["ready"]),
        "blocked_count": len(result["blocked"]),
        **result,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Valida e normaliza a entrada do template BIM IFC.")
    parser.add_argument("template", type=Path)
    args = parser.parse_args()
    try:
        if args.template.suffix.lower() != ".xlsx":
            raise ValueError("O arquivo de entrada deve ser .xlsx.")
        print(json.dumps(intake(args.template), ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, zipfile.BadZipFile) as error:
        print(json.dumps({"status": "error", "summary": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
