import re
import unittest
from pathlib import Path


class ResearcherStartTests(unittest.TestCase):
    def test_latest_quickstart_revision_matches_verification_history(self):
        root = Path(__file__).resolve().parents[1]
        guide = (root / "docs" / "RESEARCHER_START.md").read_text()
        history = (root / "docs" / "RESEARCHER_START_HISTORY.md").read_text()

        latest = guide.split("**Current public-main quickstart verification", 1)[1].split("\n\n", 1)[0]
        match = re.search(r"\]\(https://github\.com/Metivity/talk2nature/commit/([0-9a-f]{40})\)", latest)
        self.assertIsNotNone(match)
        revision = match.group(1)
        current_entry = history.splitlines()[4]
        self.assertTrue(current_entry.startswith("## Researcher-kit reproduction"))
        self.assertIn(revision[:7], current_entry)
        self.assertIn(revision, history)
        self.assertIn("not an independent reproduction", history)


if __name__ == "__main__":
    unittest.main()
