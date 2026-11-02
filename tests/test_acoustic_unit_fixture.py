import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / 'examples/acoustic-units.synthetic.json'
ANNOTATIONS = ROOT / 'examples/annotations.synthetic.json'


class AcousticUnitFixtureTests(unittest.TestCase):
    def test_fixture_is_synthetic_and_matches_annotation_recording(self):
        proposal = json.loads(FIXTURE.read_text())
        annotation = json.loads(ANNOTATIONS.read_text())
        self.assertEqual(proposal['origin'], 'synthetic')
        self.assertEqual(proposal['schema'], 'talk2nature.acoustic-unit-crosswalk.synthetic.v1')
        self.assertEqual(proposal['recording_id'], annotation['recording']['recording_id'])
        self.assertEqual(proposal['observation_fixture'], 'annotations.synthetic.json')
        self.assertEqual(proposal['model_run']['model_version'], 'not-a-real-model')
        self.assertEqual(annotation['recording']['origin'], 'synthetic')

    def test_frame_runs_form_a_bounded_nonoverlapping_lattice(self):
        proposal = json.loads(FIXTURE.read_text())
        timebase = proposal['model_run']['timebase']
        runs = proposal['model_run']['runs']
        self.assertEqual(timebase['hop_samples'] / timebase['sample_rate_hz'], 0.5)
        self.assertEqual(timebase['frame_count'] * 0.5, timebase['duration_seconds'])
        self.assertEqual(runs[0]['start_frame'], 0)
        self.assertEqual(runs[-1]['end_frame_exclusive'], timebase['frame_count'])
        for left, right in zip(runs, runs[1:]):
            self.assertEqual(left['end_frame_exclusive'], right['start_frame'])
        for run in runs:
            self.assertLess(run['start_frame'], run['end_frame_exclusive'])
            self.assertLessEqual(run['end_frame_exclusive'], timebase['frame_count'])

    def test_model_proposals_have_no_human_context_or_meaning_fields(self):
        proposal = json.loads(FIXTURE.read_text())
        forbidden = {'context', 'context_source', 'kind', 'meaning', 'translation', 'confidence'}
        self.assertTrue(forbidden.isdisjoint(proposal['model_run']))
        for run in proposal['model_run']['runs']:
            self.assertTrue(forbidden.isdisjoint(run))
        self.assertEqual(sum(r['end_frame_exclusive'] - r['start_frame'] for r in proposal['model_run']['runs']), 16)


if __name__ == '__main__':
    unittest.main()
