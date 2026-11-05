import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class AutoResearchProtocolTests(unittest.TestCase):
    def test_pipeline_comparability_is_gated_without_approving_a_run(self):
        program = (ROOT / "research/autoresearch/program.md").read_text()
        adaptation = (ROOT / "docs/AUTORESEARCH_ADAPTATION.md").read_text()
        decision = (ROOT / "docs/MODEL_DATA_DECISION.md").read_text()

        self.assertIn("Status: NOT READY", program)
        self.assertIn("No ML task, dataset, model or run is approved.", program)
        self.assertIn("passive bird-sound presence detection", decision)
        self.assertIn("whether any bird sound is present in a ten-second soundscape clip", program)
        self.assertIn("| [BirdVox-70k](../research/birdvox-70k-flight-call-detection-benchmark-2018/) |", decision)
        self.assertIn("hard negatives were mined from high-confidence false alarms", decision)
        self.assertIn("not ten-second any-bird presence", decision)
        self.assertIn("Zenodo's structured Rights field is blank", decision)
        self.assertIn("No dataset is currently selected or admitted.", program)
        self.assertIn("CEB v1.1 is metadata-only detector prior art, **not selected**", program)
        self.assertIn("no reviewed candidate clears every benchmark gate", program)
        self.assertIn("official evaluation labels are already public, not a concealed locked test", program)
        self.assertIn("known-caller classification versus unseen-caller transfer", program)
        self.assertIn("source and processing sample rates", program)
        self.assertIn("group/split membership, random seeds, class balance", program)
        self.assertIn("same question-appropriate frozen groups", program)
        self.assertIn("preprocessing changes with model changes", program)
        self.assertIn("no model or recording may be run under this section", program)
        self.assertIn("not a universal baseline", adaptation)


if __name__ == "__main__":
    unittest.main()
