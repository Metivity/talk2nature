import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class FinlandWorkflowReviewTests(unittest.TestCase):
    def test_code_deposit_has_separate_rights_and_no_acquired_files(self):
        resources = json.loads((ROOT / 'research/resources.json').read_text())['resources']
        source_records = json.loads((ROOT / 'content/sources.json').read_text())
        notes = json.loads((ROOT / 'content/research.json').read_text())
        code = next(r for r in resources if r['id'] == 'finland-citizen-audio-digital-twin-code-2025')
        code_source = next(s for s in source_records if s['id'] == 633)
        note = next(n for n in notes if n['slug'] == 'citizen-audio-digital-twin-finland-2026')

        self.assertEqual(code['kind'], 'code')
        self.assertEqual(code['rights']['license'], 'CC-BY-4.0 (declared by current Zenodo software record)')
        self.assertIn('mobile app', code['rights']['scope'])
        self.assertEqual(code['acquisition'], 'metadata_only')
        self.assertEqual(code['files'], [])
        self.assertIn('Mahti', code['review_depth'])
        self.assertEqual(code['source_ids'], [633])
        self.assertEqual(note['source_ids'], [594])
        self.assertIn('Zenodo source-code deposit', code_source['title'])
        self.assertIn('no code reproduction', note['review_stage'])

    def test_university_path_requires_a_demonstrated_gap_before_hosting(self):
        brief = (ROOT / 'docs/UNIVERSITY_EVALUATION.md').read_text()

        self.assertIn('Applied workflow comparison — November 3, 2026', brief)
        self.assertIn('do not build a shared recording network', brief)
        self.assertIn('Reconsider an adapter or hosted service only after a named research group identifies', brief)
        self.assertIn('no shared audio store', brief)
        self.assertIn('independently measured outcomes distinct', brief)


if __name__ == '__main__':
    unittest.main()
