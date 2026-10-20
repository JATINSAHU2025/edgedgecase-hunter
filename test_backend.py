import base64
import unittest

from fastapi import HTTPException
from main import ClassifyRequest, _decode_image, _normalise_model_json, _extract_output_text
import mobileclip2_provider
try:
    import torch
except ImportError:  # Optional for API-contract-only local test environments.
    torch = None


class BackendValidationTests(unittest.TestCase):
    def test_valid_jpeg_base64_is_accepted(self):
        payload = b"\xff\xd8\xff" + b"test-jpeg-body"
        request = ClassifyRequest(imageBase64=base64.b64encode(payload).decode(), mimeType="image/jpeg")
        self.assertEqual(_decode_image(request), payload)

    def test_mime_signature_mismatch_is_rejected(self):
        payload = b"not-a-real-png"
        request = ClassifyRequest(imageBase64=base64.b64encode(payload).decode(), mimeType="image/png")
        with self.assertRaises(HTTPException) as raised:
            _decode_image(request)
        self.assertEqual(raised.exception.status_code, 415)

    def test_normalises_identification_contract(self):
        result = _normalise_model_json(
            '{"name":"Brass ball valve","description":"A hand-operated valve.",'
            '"visibleFeatures":["red lever","threaded brass body"],'
            '"alternatives":["ball valve","plumbing fitting",""],'
            '"uncertainty":"medium","detectedText":""}'
        )
        self.assertEqual(result["name"], "Brass ball valve")
        self.assertEqual(result["visibleFeatures"], ["red lever", "threaded brass body"])
        self.assertEqual(result["alternatives"], ["plumbing fitting"])
        self.assertEqual(result["uncertainty"], "medium")

    def test_missing_name_is_rejected(self):
        with self.assertRaises(HTTPException) as raised:
            _normalise_model_json('{"description":"No actual object name."}')
        self.assertEqual(raised.exception.status_code, 502)

    def test_extracts_interactions_output_text(self):
        response = {
            "output": [{
                "type": "message",
                "content": [{"type": "text", "text": '{"name":"Basin"}'}]
            }]
        }
        self.assertEqual(_extract_output_text(response), '{"name":"Basin"}')

    def test_prefers_documented_output_text(self):
        self.assertEqual(
            _extract_output_text({"output_text": '  {"name":"Basin"}  '}),
            '{"name":"Basin"}'
        )

    @unittest.skipIf(torch is None, "PyTorch is installed in the Docker runtime; skip embedding test without it")
    def test_catalog_matches_deduplicate_multiple_views_of_same_product(self):
        old_catalog = mobileclip2_provider._catalog_state
        try:
            mobileclip2_provider._catalog_state = {
                "embeddings": torch.tensor([[1.0, 0.0], [0.99, 0.01], [0.0, 1.0]]),
                "products": [
                    {"product_id": "A", "sku": "A-1", "name": "Basin", "price": "1000"},
                    {"product_id": "A", "sku": "A-1", "name": "Basin", "price": "1000"},
                    {"product_id": "B", "sku": "B-1", "name": "Tap", "price": "250"},
                ],
            }
            matches = mobileclip2_provider._catalog_matches(torch.tensor([[1.0, 0.0]]), {"torch": torch}, limit=5)
            self.assertEqual([m["productId"] for m in matches], ["A", "B"])
            self.assertEqual(matches[0]["name"], "Basin")
            self.assertGreater(matches[0]["similarity"], matches[1]["similarity"])
        finally:
            mobileclip2_provider._catalog_state = old_catalog


if __name__ == "__main__":
    unittest.main()
