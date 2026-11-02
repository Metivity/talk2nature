import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class BioacousticLifecycleReviewTest(unittest.TestCase):
    def test_review_is_linked_to_model_learning_and_candidate_gates(self):
        notes = json.loads((ROOT / "content/research.json").read_text())
        note = next(row for row in notes if row["slug"] == "twelve-quick-tips-bioacoustic-deep-learning-2026")
        self.assertEqual(note["source_ids"], [618])
        self.assertIn("hard negatives", note["lesson"])
        self.assertIn("NOT READY", note["lesson"])
        learning = json.loads((ROOT / "content/learning-paths.json").read_text())
        model = next(row for row in learning["paths"] if row["id"] == "model")
        self.assertIn(note["slug"], model["notes"])
        card = (ROOT / "docs/BENCHMARK_CANDIDATE_RUN_CARD.md").read_text()
        self.assertIn("Field-lifecycle checklist", card)
        self.assertIn("pretraining overlap", card)
        self.assertIn("real-device checks", card)

    def test_article_metadata_is_not_data_or_model_admission(self):
        catalog = json.loads((ROOT / "research/resources.json").read_text())
        resource = next(row for row in catalog["resources"] if row["id"] == "twelve-quick-tips-animal-sound-ml-2026")
        self.assertEqual(resource["kind"], "paper")
        self.assertEqual(resource["acquisition"], "metadata_only")
        self.assertEqual(resource["files"], [])
        self.assertIn("linked data, code", resource["rights"]["scope"])


if __name__ == "__main__":
    unittest.main()
