#!/usr/bin/env python3
"""Local, content-safe LGPD preflight for IFC workflow inputs.

The scanner never prints matched values or text excerpts. It emits only a file
digest, coarse finding categories and counts so its JSON can safely be passed to
an LLM-based orchestrator.
"""

from __future__ import annotations

import argparse
import codecs
import hashlib
import json
import re
import sys
import zipfile
from collections import Counter
from pathlib import Path
from typing import BinaryIO, Iterable


TEXT_EXTENSIONS = {
    ".bcf", ".csv", ".ifc", ".ifcxml", ".ids", ".json", ".md",
    ".step", ".txt", ".xml", ".yaml", ".yml",
}
OOXML_EXTENSIONS = {".docx", ".pptx", ".xlsx"}
OPAQUE_EXTENSIONS = {".pdf", ".dwg", ".rvt", ".nwc", ".nwd"}
FORMAT_LABELS = {
    **{extension: "text" for extension in TEXT_EXTENSIONS},
    **{extension: "ooxml" for extension in OOXML_EXTENSIONS},
    **{extension: "opaque" for extension in OPAQUE_EXTENSIONS},
}
CHUNK_SIZE = 1024 * 1024
OVERLAP = 512
MAX_OOXML_ENTRIES = 10_000
MAX_OOXML_ENTRY_SIZE = 32 * 1024 * 1024
MAX_OOXML_TOTAL_SIZE = 256 * 1024 * 1024
MAX_OOXML_RATIO = 200


BYTE_PATTERNS = {
    "email": re.compile(rb"(?i)(?<![\w.+-])[\w.+-]{1,64}@[a-z0-9.-]{1,190}\.[a-z]{2,24}(?![\w.-])"),
    "formatted_phone_br": re.compile(rb"(?<!\d)(?:\+?55[ .-]?)?\(?[1-9]{2}\)?[ .-]?9?\d{4}[ .-]?\d{4}(?!\d)"),
    "ifc_person_entity": re.compile(rb"(?i)\bIFCPERSON\s*\("),
    "ifc_person_and_organization": re.compile(rb"(?i)\bIFCPERSONANDORGANIZATION\s*\("),
    "ooxml_creator_metadata": re.compile(rb"(?i)<(?:dc:creator|cp:lastModifiedBy)\b"),
    "personal_identifier_field": re.compile(
        rb"(?i)[\"'<\s](?:cpf|rg|pis|pasep|employee[_ -]?id|matricula[_ -]?(?:funcional|empregado))"
        rb"[\"'>:\s]"
    ),
}
TEXT_PATTERNS = {
    category: re.compile(pattern.pattern.decode("ascii"), pattern.flags)
    for category, pattern in BYTE_PATTERNS.items()
}


def valid_cpf(digits: bytes) -> bool:
    if len(digits) != 11 or len(set(digits)) == 1:
        return False
    nums = [value - 48 for value in digits]
    for size in (9, 10):
        total = sum(nums[index] * (size + 1 - index) for index in range(size))
        check = (total * 10 % 11) % 10
        if check != nums[size]:
            return False
    return True


CPF_CANDIDATE = re.compile(rb"(?<!\d)(\d{3}[. -]?\d{3}[. -]?\d{3}[- ]?\d{2})(?!\d)")


class BinaryTextError(ValueError):
    pass


def scan_stream(
    stream: BinaryIO,
    *,
    digest: "hashlib._Hash | None" = None,
    validate_utf8: bool = False,
) -> Counter[str]:
    findings: Counter[str] = Counter()
    tail = b""
    decoder = codecs.getincrementaldecoder("utf-8")(errors="strict") if validate_utf8 else None
    while chunk := stream.read(CHUNK_SIZE):
        if digest is not None:
            digest.update(chunk)
        if validate_utf8:
            if b"\x00" in chunk:
                raise BinaryTextError("NUL in textual input")
            assert decoder is not None
            decoder.decode(chunk)
        data = tail + chunk
        cutoff = len(tail)
        for category, pattern in BYTE_PATTERNS.items():
            count = sum(1 for match in pattern.finditer(data) if match.end() > cutoff)
            if count:
                findings[category] += count
        cpf_count = sum(
            1
            for match in CPF_CANDIDATE.finditer(data)
            if match.end() > cutoff and valid_cpf(re.sub(rb"\D", b"", match.group(1)))
        )
        if cpf_count:
            findings["cpf"] += cpf_count
        tail = data[-OVERLAP:]
    if decoder is not None:
        decoder.decode(b"", final=True)
    return findings


def scan_unicode_stream(
    stream: BinaryIO, encoding: str, *, digest: "hashlib._Hash | None" = None
) -> Counter[str]:
    findings: Counter[str] = Counter()
    decoder = codecs.getincrementaldecoder(encoding)(errors="strict")
    tail = ""
    while chunk := stream.read(CHUNK_SIZE):
        if digest is not None:
            digest.update(chunk)
        text = tail + decoder.decode(chunk)
        cutoff = len(tail)
        for category, pattern in TEXT_PATTERNS.items():
            count = sum(1 for match in pattern.finditer(text) if match.end() > cutoff)
            if count:
                findings[category] += count
        cpf_count = sum(
            1
            for match in re.finditer(r"(?<!\d)(\d{3}[. -]?\d{3}[. -]?\d{3}[- ]?\d{2})(?!\d)", text)
            if match.end() > cutoff and valid_cpf(re.sub(r"\D", "", match.group(1)).encode("ascii"))
        )
        if cpf_count:
            findings["cpf"] += cpf_count
        tail = text[-OVERLAP:]
    decoder.decode(b"", final=True)
    return findings


def scan_content(
    stream: BinaryIO,
    extension: str | None = None,
    *,
    digest: "hashlib._Hash | None" = None,
) -> tuple[Counter[str], list[str]]:
    prefix = stream.read(4096)
    stream.seek(0)
    try:
        if prefix.startswith((codecs.BOM_UTF16_LE, codecs.BOM_UTF16_BE)):
            decoded_prefix = prefix.decode("utf-16", errors="strict").lstrip()
            if extension in {".ifc", ".step"} and not decoded_prefix.startswith("ISO-10303-21"):
                return Counter(), ["invalid_step_signature"]
            return scan_unicode_stream(stream, "utf-16", digest=digest), []
        if extension in {".ifc", ".step"} and not prefix.lstrip().startswith(b"ISO-10303-21"):
            return Counter(), ["invalid_step_signature"]
        return scan_stream(stream, digest=digest, validate_utf8=True), []
    except BinaryTextError:
        return Counter(), ["binary_content_in_text_format"]
    except UnicodeError:
        return Counter(), ["unsupported_or_invalid_text_encoding"]


def merge_counts(target: Counter[str], source: Counter[str]) -> None:
    for category, count in source.items():
        if count:
            target[category] += count


def scan_ooxml(stream: BinaryIO) -> tuple[Counter[str], list[str]]:
    findings: Counter[str] = Counter()
    limitations: list[str] = []
    try:
        with zipfile.ZipFile(stream) as archive:
            entries = archive.infolist()
            if len(entries) > MAX_OOXML_ENTRIES:
                return findings, ["ooxml_entry_limit_exceeded"]
            total_size = 0
            for entry in entries:
                if entry.is_dir():
                    continue
                if not entry.filename.lower().endswith((".xml", ".rels")):
                    return Counter(), ["ooxml_uninspected_payload"]
                total_size += entry.file_size
                ratio = entry.file_size / max(entry.compress_size, 1)
                if entry.file_size > MAX_OOXML_ENTRY_SIZE or total_size > MAX_OOXML_TOTAL_SIZE or ratio > MAX_OOXML_RATIO:
                    return Counter(), ["ooxml_decompression_limit_exceeded"]
                with archive.open(entry) as stream:
                    entry_findings, entry_limits = scan_content(stream)
                    if entry_limits:
                        return Counter(), entry_limits
                    merge_counts(findings, entry_findings)
    except (OSError, zipfile.BadZipFile, RuntimeError):
        limitations.append("invalid_or_encrypted_ooxml")
    return findings, limitations


def decision_for(extension: str, findings: Counter[str], limitations: Iterable[str]) -> tuple[str, list[str]]:
    reasons: list[str] = []
    limitations = list(limitations)
    if limitations:
        reasons.extend(limitations)
        return "REVIEW", reasons
    if findings:
        reasons.extend(sorted(findings))
        return "BLOCK", reasons
    if extension in OPAQUE_EXTENSIONS or extension not in TEXT_EXTENSIONS | OOXML_EXTENSIONS:
        return "REVIEW", ["content_not_fully_inspectable"]
    return "ALLOW", []


def scan_file(path: Path, root: Path | None = None) -> dict[str, object]:
    extension = path.suffix.lower()
    findings: Counter[str] = Counter()
    limitations: list[str] = []

    try:
        resolved = path.resolve(strict=True)
        if path.is_symlink() or (root is not None and not resolved.is_relative_to(root.resolve(strict=True))):
            raise ValueError("unsafe_input_path")
    except (OSError, ValueError):
        return {
            "status": "error",
            "decision": "BLOCK",
            "reason_codes": ["unsafe_input_path"],
            "findings": [],
            "safe_to_forward": False,
        }

    if not resolved.is_file():
        return {
            "status": "error",
            "decision": "BLOCK",
            "reason_codes": ["input_not_regular_file"],
            "findings": [],
            "safe_to_forward": False,
        }

    digest = hashlib.sha256()
    scan_digest = hashlib.sha256()
    before = resolved.stat()
    with resolved.open("rb") as stream:
        while chunk := stream.read(CHUNK_SIZE):
            digest.update(chunk)
        stream.seek(0)
        if extension in OOXML_EXTENSIONS:
            findings, limitations = scan_ooxml(stream)
        elif extension in TEXT_EXTENSIONS:
            findings, limitations = scan_content(stream, extension, digest=scan_digest)
        else:
            findings = scan_stream(stream, digest=scan_digest)
    if extension in OOXML_EXTENSIONS:
        with resolved.open("rb") as verification_stream:
            while chunk := verification_stream.read(CHUNK_SIZE):
                scan_digest.update(chunk)
    if digest.digest() != scan_digest.digest():
        limitations.append("input_changed_during_scan")
    after = resolved.stat()
    if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
        if "input_changed_during_scan" not in limitations:
            limitations.append("input_changed_during_scan")

    decision, reasons = decision_for(extension, findings, limitations)
    return {
        "status": "success",
        "policy_version": "lgpd-preflight-1.0",
        "decision": decision,
        "sha256": digest.hexdigest(),
        "format": FORMAT_LABELS.get(extension, "unknown"),
        "findings": [
            {"category": category, "count": findings[category]}
            for category in sorted(findings)
            if findings[category]
        ],
        "reason_codes": reasons,
        "safe_to_forward": decision == "ALLOW",
        "content_excerpts_returned": False,
        "limitations": limitations,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Executa preflight LGPD local sem expor valores encontrados."
    )
    parser.add_argument("input", type=Path, help="Arquivo local a inspecionar")
    parser.add_argument("--root", type=Path, help="Raiz autorizada; caminhos externos e links são bloqueados")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        result = scan_file(args.input, args.root)
    except (OSError, ValueError) as exc:
        result = {
            "status": "error",
            "decision": "BLOCK",
            "reason_codes": [f"scanner_error:{type(exc).__name__}"],
            "findings": [],
            "safe_to_forward": False,
            "content_excerpts_returned": False,
        }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return {"ALLOW": 0, "REVIEW": 2, "BLOCK": 3}.get(str(result.get("decision")), 4)


if __name__ == "__main__":
    sys.exit(main())
