import os
import unittest
from unittest.mock import MagicMock

from engeff import jev
from engeff.scale import LEVELS

RESPONSE = {
    "model": "jev-1.14.0",
    "usage": {"input_tokens": 3, "output_tokens": 1},
    "answers": {"effort": {"type": "score", "score": 1.43, "confidence": 0.35,
                           "probabilities": {"0": 0.0, "1": 0.57, "2": 0.43, "3": 0.0}}},
}


class JevTest(unittest.TestCase):
    def test_payload_has_one_score_question_with_four_levels(self):
        q = jev.build_payload("text", "jev-latest")["questions"]["effort"]
        self.assertEqual(q["type"], "score")
        self.assertEqual(q["criteria"], LEVELS)
        self.assertEqual(len(LEVELS), 4)

    def test_response_is_mapped_to_the_shared_record(self):
        resp = MagicMock(status_code=200)
        resp.json.return_value = RESPONSE
        http = MagicMock()
        http.post.return_value = resp
        os.environ["TYPESAFE_API_KEY"] = "test"
        rec = jev.score_issue({"instance_id": "a-1", "problem_statement": "x"}, session=http)
        self.assertEqual(rec["score"], 1)
        self.assertAlmostEqual(rec["score_raw"], 1.43)
        self.assertIsNone(rec["reason"])


if __name__ == "__main__":
    unittest.main()
