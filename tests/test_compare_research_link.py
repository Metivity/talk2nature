import unittest
from pathlib import Path


class CompareResearchLinkTests(unittest.TestCase):
    def test_compare_explains_the_boundary_between_observation_and_meaning(self):
        project_root = Path(__file__).resolve().parents[1]
        compare = (project_root / 'web' / 'templates' / 'compare.html').read_text()
        self.assertIn('It does not measure pitch, identify calls, or infer what an animal meant.', compare)
        self.assertIn('An observation is not a translation;', compare)
        self.assertIn('review of a disputed bonobo call-combination claim', compare)
        self.assertIn('href="{{base}}/research/bonobo-compositionality-critique-2026/"', compare)
        self.assertIn('The original paper and a later published critique disagree about what the data support.', compare)


if __name__ == '__main__':
    unittest.main()
