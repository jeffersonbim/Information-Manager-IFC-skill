#!/usr/bin/env python3
"""Create a privacy-cleared, content-addressed snapshot before any LLM sees it."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

try:
    from .privacy_gate import FORMAT_LABELS, scan_file
except ImportError:  # Direct CLI execution from scripts/.
    from privacy_gate import FORMAT_LABELS, scan_file


def ingest(source: Path, cleared_root: Path) -> dict[str, object]:
    cleared_root.mkdir(parents=True, exist_ok=True)
    extension = source.suffix.lower()
    safe_extension = extension if extension in FORMAT_LABELS else ".bin"
    temporary_path: Path | None = None
    try:
        with source.open("rb") as input_stream, tempfile.NamedTemporaryFile(
            mode="wb", dir=cleared_root, prefix=".privacy-", suffix=safe_extension, delete=False
        ) as snapshot:
            temporary_path = Path(snapshot.name)
            shutil.copyfileobj(input_stream, snapshot, length=1024 * 1024)
            snapshot.flush()
            os.fsync(snapshot.fileno())

        result = scan_file(temporary_path, cleared_root)
        if result.get("decision") != "ALLOW":
            return result

        artifact_id = str(result["sha256"])
        destination = cleared_root / f"{artifact_id}{safe_extension}"
        if destination.exists():
            existing = scan_file(destination, cleared_root)
            if existing.get("sha256") != artifact_id or existing.get("decision") != "ALLOW":
                return {
                    "status": "error",
                    "decision": "BLOCK",
                    "reason_codes": ["content_address_collision"],
                    "findings": [],
                    "safe_to_forward": False,
                    "content_excerpts_returned": False,
                }
            temporary_path.unlink()
            temporary_path = None
        else:
            temporary_path.replace(destination)
            temporary_path = None

        manifest = {
            **result,
            "artifact_id": artifact_id,
            "agent_path": f"/dados-ifc/cleared/{artifact_id}{safe_extension}",
        }
        manifest_path = cleared_root / f"{artifact_id}.privacy.json"
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        return manifest
    except (OSError, ValueError) as exc:
        return {
            "status": "error",
            "decision": "BLOCK",
            "reason_codes": [f"ingest_error:{type(exc).__name__}"],
            "findings": [],
            "safe_to_forward": False,
            "content_excerpts_returned": False,
        }
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Copia localmente apenas entradas liberadas pelo preflight LGPD.")
    parser.add_argument("input", type=Path, help="Arquivo original; o nome nunca aparece na saída")
    parser.add_argument("--cleared-root", type=Path, required=True, help="Diretório local montado como /dados-ifc/cleared")
    args = parser.parse_args()
    result = ingest(args.input, args.cleared_root)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return {"ALLOW": 0, "REVIEW": 2, "BLOCK": 3}.get(str(result.get("decision")), 4)


if __name__ == "__main__":
    sys.exit(main())
