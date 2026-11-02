import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class AutoResearchProtocolTests(unittest.TestCase):
    def test_pipeline_comparability_is_gated_without_approving_a_run(self):
        program = (ROOT / "research/autoresearch/program.md").read_text()
        adaptation = (ROOT / "docs/AUTORESEARCH_ADAPTATION.md").read_text()

        self.assertIn("Status: NOT READY", program)
        self.assertIn("known-caller classification versus unseen-caller transfer", program)
        self.assertIn("source and processing sample rates", program)
        self.assertIn("group/split membership, random seeds, class balance", program)
        self.assertIn("same question-appropriate frozen groups", program)
        self.assertIn("preprocessing changes with model changes", program)
        self.assertIn("no model or recording may be run under this section", program)
        self.assertIn("not a universal baseline", adaptation)


if __name__ == "__main__":
    unittest.main()
