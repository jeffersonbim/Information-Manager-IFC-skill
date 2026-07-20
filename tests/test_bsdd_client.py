import json
import unittest
from io import StringIO
from pathlib import Path
from sys import path
from urllib.error import HTTPError

path.insert(0, str(Path(__file__).parents[1] / "scripts"))
from bsdd_client import BsddClient, BsddError, USER_AGENT, main


class Response:
    def __enter__(self): return self
    def __exit__(self, *_): return False
    def read(self): return json.dumps({"ok": True}).encode()


class BsddClientTests(unittest.TestCase):
    def test_array_parameters_and_headers(self):
        seen = {}
        def opener(request, timeout):
            seen.update(url=request.full_url, headers=dict(request.header_items()), timeout=timeout)
            return Response()
        data = BsddClient(opener=opener).search_classes("wall", ["urn:a", "urn:b"], ["IfcWall"])
        self.assertTrue(data["ok"])
        self.assertIn("DictionaryUris=urn%3Aa&DictionaryUris=urn%3Ab", seen["url"])
        self.assertEqual(seen["headers"]["User-agent"], USER_AGENT)
        self.assertEqual(seen["headers"]["X-user-agent"], USER_AGENT)

    def test_invalid_page_rejected_before_request(self):
        with self.assertRaises(ValueError): BsddClient().dictionaries(limit=0)

    def test_http_error_is_controlled(self):
        def opener(request, timeout): raise HTTPError(request.full_url, 503, "down", {}, None)
        with self.assertRaisesRegex(BsddError, "HTTP 503"):
            BsddClient(opener=opener).dictionaries()

    def test_cli_output_follows_common_contract(self):
        from unittest.mock import patch
        output = StringIO()
        with patch.object(BsddClient, "dictionaries", return_value={"dictionaries": []}), patch("sys.stdout", output):
            self.assertEqual(main(["dictionaries", "--limit", "1"]), 0)
        payload = json.loads(output.getvalue())
        for key in ("findings", "evidence", "artifacts", "limitations", "next_actions", "requires_human_approval"):
            self.assertIn(key, payload)


if __name__ == "__main__": unittest.main()
