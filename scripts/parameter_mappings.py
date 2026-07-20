#!/usr/bin/env python3
"""Query the authorized Revit/IFC and COBie parameter mapping sources."""

from __future__ import annotations

import argparse
import json
from collections import Counter, namedtuple
from pathlib import Path
from typing import Iterable, Iterator


Source = namedtuple("Source", "path kind scope")


def default_source_dir() -> Path:
    return Path(__file__).parents[1] / "references" / "parameter-mappings" / "sources"


def authorized_sources(root: Path) -> tuple[Source, ...]:
    """Return the fixed allowlist. IFC-SG is intentionally not accepted."""
    return (
        Source(root / "IFC Shared Parameters-RevitIFCBuiltIn_ALL.txt", "revit-shared", "instance"),
        Source(root / "IFC Shared Parameters-RevitIFCBuiltIn-Type_ALL.txt", "revit-shared", "type"),
        Source(root / "DefaultUserDefinedParameterSets.txt", "user-defined-pset", None),
        Source(root / "IFC2x3 COBie 2.4 Design Deliverable.txt", "cobie-ifc2x3", None),
    )


def read_lines(path: Path) -> list[str]:
    data = path.read_bytes()
    for encoding in ("utf-8-sig", "utf-16", "cp1252"):
        try:
            return data.decode(encoding).splitlines()
        except UnicodeDecodeError:
            continue
    raise ValueError(f"Unsupported text encoding: {path}")


def parse_revit_shared_parameters(path: Path, scope: str) -> Iterator[dict]:
    groups: dict[str, str] = {}
    for line_number, raw_line in enumerate(read_lines(path), start=1):
        if raw_line.startswith("GROUP\t"):
            parts = raw_line.split("\t", 2)
            if len(parts) == 3:
                groups[parts[1]] = parts[2].strip()
            continue
        if not raw_line.startswith("PARAM\t"):
            continue

        parts = raw_line.split("\t")
        parts.extend([""] * (9 - len(parts)))
        _, guid, name, revit_datatype, data_category, group_id, visible, description, user_modifiable = parts[:9]
        normalized_name = name.removesuffix("[Type]")
        property_set, separator, property_name = normalized_name.rpartition(".")
        if not separator:
            property_set = groups.get(group_id, "")
            property_name = normalized_name

        yield {
            "source_kind": "revit-shared",
            "source_file": path.name,
            "source_line": line_number,
            "scope": scope,
            "property_set": property_set,
            "property": property_name,
            "revit_parameter": name,
            "guid": guid,
            "revit_datatype": revit_datatype,
            "ifc_datatype": description,
            "data_category": data_category,
            "group": groups.get(group_id, ""),
            "visible": visible == "1",
            "user_modifiable": user_modifiable == "1",
            "applicable_entities": [],
        }


def parse_property_sets(path: Path, source_kind: str) -> Iterator[dict]:
    current: dict | None = None
    for line_number, raw_line in enumerate(read_lines(path), start=1):
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("PropertySet:"):
            parts = stripped.split("\t")
            parts.extend([""] * (4 - len(parts)))
            scope_code = parts[2].strip().upper()
            current = {
                "property_set": parts[1].strip(),
                "scope": {"I": "instance", "T": "type"}.get(scope_code, "unspecified"),
                "applicable_entities": [item.strip() for item in parts[3].split(",") if item.strip()],
            }
            continue
        if current is None:
            continue

        parts = stripped.split("\t")
        parts = [part.strip() for part in parts]
        parts.extend([""] * (3 - len(parts)))
        property_name, datatype, revit_parameter = parts[:3]
        if not property_name:
            continue
        yield {
            "source_kind": source_kind,
            "source_file": path.name,
            "source_line": line_number,
            "scope": current["scope"],
            "property_set": current["property_set"],
            "property": property_name,
            "revit_parameter": revit_parameter or property_name,
            "guid": "",
            "revit_datatype": "",
            "ifc_datatype": datatype,
            "data_category": "",
            "group": "",
            "visible": None,
            "user_modifiable": None,
            "applicable_entities": current["applicable_entities"],
        }


def load_records(root: Path | None = None) -> Iterator[dict]:
    source_root = root or default_source_dir()
    for source in authorized_sources(source_root):
        if not source.path.is_file():
            raise FileNotFoundError(f"Authorized mapping source not found: {source.path}")
        if source.kind == "revit-shared":
            yield from parse_revit_shared_parameters(source.path, source.scope)
        else:
            yield from parse_property_sets(source.path, source.kind)


def search_records(
    records: Iterable[dict],
    query: str,
    *,
    scope: str | None = None,
    source_kind: str | None = None,
    limit: int = 20,
) -> list[dict]:
    needle = query.casefold().strip()
    matches: list[dict] = []
    for record in records:
        if scope and record["scope"] != scope:
            continue
        if source_kind and record["source_kind"] != source_kind:
            continue
        searchable = " ".join(
            [
                record["property_set"],
                record["property"],
                record["revit_parameter"],
                record["guid"],
                record["ifc_datatype"],
                record["group"],
                *record["applicable_entities"],
            ]
        ).casefold()
        if needle in searchable:
            matches.append(record)
            if len(matches) >= limit:
                break
    return matches


def build_stats(records: Iterable[dict]) -> dict:
    source_counts: Counter[str] = Counter()
    scope_counts: Counter[str] = Counter()
    kind_counts: Counter[str] = Counter()
    total = 0
    for record in records:
        total += 1
        source_counts[record["source_file"]] += 1
        scope_counts[record["scope"]] += 1
        kind_counts[record["source_kind"]] += 1
    return {
        "authorized_source_count": 4,
        "record_count": total,
        "records_by_source": dict(sorted(source_counts.items())),
        "records_by_scope": dict(sorted(scope_counts.items())),
        "records_by_kind": dict(sorted(kind_counts.items())),
        "excluded_sources": ["IFC-SG Property Mapping Export.txt"],
    }


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, default=default_source_dir())
    subparsers = parser.add_subparsers(dest="command", required=True)

    query_parser = subparsers.add_parser("query", help="Search the authorized mappings")
    query_parser.add_argument("query")
    query_parser.add_argument("--scope", choices=("instance", "type", "unspecified"))
    query_parser.add_argument(
        "--source-kind", choices=("revit-shared", "user-defined-pset", "cobie-ifc2x3")
    )
    query_parser.add_argument("--limit", type=int, default=20)

    subparsers.add_parser("stats", help="Show source and record counts")
    return parser


def main() -> int:
    args = create_parser().parse_args()
    if args.command == "stats":
        payload = build_stats(load_records(args.source_dir))
    else:
        payload = {
            "query": args.query,
            "scope": args.scope,
            "source_kind": args.source_kind,
            "results": search_records(
                load_records(args.source_dir),
                args.query,
                scope=args.scope,
                source_kind=args.source_kind,
                limit=max(1, args.limit),
            ),
        }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
