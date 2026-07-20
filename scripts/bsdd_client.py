#!/usr/bin/env python3
"""Cliente CLI somente leitura para a API pública buildingSMART Data Dictionary."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

BASE_URL = "https://api.bsdd.buildingsmart.org"
USER_AGENT = "Information-Manager-IFC-skill/2.0 (bsdd-read-client)"


class BsddError(RuntimeError):
    """Erro controlado de integração com o bSDD."""


class BsddClient:
    def __init__(self, base_url: str = BASE_URL, timeout: float = 30, opener: Callable = urlopen):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.opener = opener
        self.last_requested_url: str | None = None

    def _get(self, path: str, params: dict[str, Any]) -> Any:
        clean = {key: value for key, value in params.items() if value is not None}
        url = f"{self.base_url}{path}?{urlencode(clean, doseq=True)}"
        self.last_requested_url = url
        request = Request(url, headers={"Accept": "application/json", "User-Agent": USER_AGENT, "X-User-Agent": USER_AGENT})
        try:
            with self.opener(request, timeout=self.timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            raise BsddError(f"bSDD retornou HTTP {exc.code} para {path}") from exc
        except URLError as exc:
            raise BsddError(f"Falha de conexão com bSDD: {exc.reason}") from exc
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise BsddError("Resposta bSDD não é JSON válido") from exc

    @staticmethod
    def _page(offset: int, limit: int) -> None:
        if offset < 0 or not 1 <= limit <= 1000:
            raise ValueError("offset deve ser >= 0 e limit deve estar entre 1 e 1000")

    def dictionaries(self, uri: str | None = None, include_test: bool = False, offset: int = 0, limit: int = 100) -> Any:
        self._page(offset, limit)
        return self._get("/api/Dictionary/v1", {"Uri": uri, "IncludeTestDictionaries": include_test, "Offset": offset, "Limit": limit})

    def search_classes(self, search_text: str, dictionary_uris: list[str] | None = None, related_ifc_entities: list[str] | None = None, offset: int = 0, limit: int = 100) -> Any:
        self._page(offset, limit)
        return self._get("/api/Class/Search/v1", {"SearchText": search_text, "DictionaryUris": dictionary_uris, "RelatedIfcEntities": related_ifc_entities, "Offset": offset, "Limit": limit})

    def get_class(self, uri: str, language_code: str | None = None) -> Any:
        return self._get("/api/Class/v1", {"Uri": uri, "IncludeClassProperties": True, "IncludeChildClassReferences": True, "IncludeClassRelations": True, "IncludeReverseRelations": False, "languageCode": language_code})

    def class_properties(self, class_uri: str, search_text: str | None = None, offset: int = 0, limit: int = 100, language_code: str | None = None) -> Any:
        self._page(offset, limit)
        return self._get("/api/Class/Properties/v1", {"ClassUri": class_uri, "SearchText": search_text, "Offset": offset, "Limit": limit, "languageCode": language_code})

    def get_property(self, uri: str, language_code: str | None = None) -> Any:
        return self._get("/api/Property/v5", {"uri": uri, "languageCode": language_code})

    def text_search(self, search_text: str, dictionary_uris: list[str] | None = None, type_filter: str | None = None, offset: int = 0, limit: int = 100) -> Any:
        self._page(offset, limit)
        return self._get("/api/TextSearch/v2", {"SearchText": search_text, "DictionaryUris": dictionary_uris, "TypeFilter": type_filter, "OnlyLatestVersion": True, "OnlyVerified": False, "IncludeInactive": False, "IncludePreview": False, "IncludeSearchDescriptions": True, "Offset": offset, "Limit": limit})


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description="Consulta somente leitura à API bSDD")
    sub = root.add_subparsers(dest="command", required=True)
    page_parent = argparse.ArgumentParser(add_help=False)
    page_parent.add_argument("--offset", type=int, default=0)
    page_parent.add_argument("--limit", type=int, default=100)
    p = sub.add_parser("dictionaries", parents=[page_parent]); p.add_argument("--uri"); p.add_argument("--include-test", action="store_true")
    p = sub.add_parser("search-classes", parents=[page_parent]); p.add_argument("search_text"); p.add_argument("--dictionary-uri", action="append"); p.add_argument("--ifc-entity", action="append")
    p = sub.add_parser("class"); p.add_argument("uri"); p.add_argument("--language")
    p = sub.add_parser("class-properties", parents=[page_parent]); p.add_argument("class_uri"); p.add_argument("--search-text"); p.add_argument("--language")
    p = sub.add_parser("property"); p.add_argument("uri"); p.add_argument("--language")
    p = sub.add_parser("text-search", parents=[page_parent]); p.add_argument("search_text"); p.add_argument("--dictionary-uri", action="append"); p.add_argument("--type-filter")
    return root


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    client = BsddClient()
    try:
        if args.command == "dictionaries": data = client.dictionaries(args.uri, args.include_test, args.offset, args.limit)
        elif args.command == "search-classes": data = client.search_classes(args.search_text, args.dictionary_uri, args.ifc_entity, args.offset, args.limit)
        elif args.command == "class": data = client.get_class(args.uri, args.language)
        elif args.command == "class-properties": data = client.class_properties(args.class_uri, args.search_text, args.offset, args.limit, args.language)
        elif args.command == "property": data = client.get_property(args.uri, args.language)
        else: data = client.text_search(args.search_text, args.dictionary_uri, args.type_filter, args.offset, args.limit)
        result = {"status": "success", "specialist": "bsdd", "summary": f"Consulta {args.command} concluída", "findings": [], "evidence": [{"source": client.last_requested_url, "accessed_at": datetime.now(timezone.utc).isoformat(), "api_contract": "buildingSMART Dictionaries v1"}], "artifacts": [], "data": data, "limitations": [], "next_actions": [], "requires_human_approval": False}
        code = 0
    except (BsddError, ValueError) as exc:
        result = {"status": "error", "specialist": "bsdd", "summary": str(exc), "findings": [], "evidence": [], "artifacts": [], "data": None, "limitations": ["A consulta não foi concluída"], "next_actions": ["Verificar parâmetros, conectividade e disponibilidade da API"], "requires_human_approval": False}
        code = 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return code


if __name__ == "__main__":
    sys.exit(main())
