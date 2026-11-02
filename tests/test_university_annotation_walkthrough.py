import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class UniversityAnnotationWalkthroughTests(unittest.TestCase):
    def test_example_applies_multi_annotator_methods_without_claiming_data(self):
        template = (ROOT / "web/templates/university.html").read_text()
        css = (ROOT / "web/assets/university.css").read_text()
        guide = (ROOT / "docs/ANNOTATION_CONTRIBUTOR_WALKTHROUGH.md").read_text()

        self.assertIn("APPLYING MULTI-ANNOTATOR RESEARCH", template)
        self.assertIn("not a recording, observation or model result", template)
        self.assertIn("No silent majority vote.", template)
        self.assertIn("blue-whale-multi-annotator-labels-2024/", template)
        self.assertIn("ANNOTATION_CONTRIBUTOR_WALKTHROUGH.md", template)
        self.assertIn("@media(max-width:700px){.university-label-grid{grid-template-columns:1fr}", css)
        self.assertIn("No real-data intake or cloud storage was added", guide)


if __name__ == "__main__":
    unittest.main()
