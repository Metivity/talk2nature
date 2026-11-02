import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / 'examples/annotation-lineage.synthetic.v1.json'
LOSS_REPORT = ROOT / 'examples/annotation-lineage-loss-report.synthetic.v1.json'


class AnnotationLineageFixtureTests(unittest.TestCase):
    def setUp(self):
        self.package = json.loads(PACKAGE.read_text())
        self.loss = json.loads(LOSS_REPORT.read_text())

    def test_observer_annotations_are_separate_and_synthetic(self):
        self.assertEqual(self.package['schema'], 'talk2nature.annotation-lineage.synthetic.v1')
        self.assertEqual(self.package['origin'], 'synthetic')
        self.assertFalse(self.package['recording_payload_present'])
        self.assertEqual(len(self.package['observer_annotations']), 2)
        for observer in self.package['observer_annotations']:
            self.assertEqual(observer['role'], 'independent_observer')
            path = ROOT / 'examples' / observer['path']
            annotation = json.loads(path.read_text())
            self.assertEqual(annotation['recording']['origin'], 'synthetic')
            self.assertEqual(annotation['recording']['annotator_id'], observer['annotator_id'])
        ids = {x['annotator_id'] for x in self.package['observer_annotations']}
        self.assertEqual(len(ids), 2)

    def test_review_preserves_disagreement_without_claiming_a_shared_event(self):
        review = self.package['review_decision']
        self.assertEqual(review['status'], 'example_only')
        self.assertEqual(review['action'], 'preserve_independent_labels')
        self.assertEqual(review['same_biological_event'], 'not_determined')
        self.assertIsNone(review['consensus_label'])

    def test_model_proposal_is_invented_unexecuted_and_nonsemantic(self):
        model = self.package['model_proposal']
        proposal = json.loads((ROOT / 'examples' / model['path']).read_text())
        self.assertEqual(model['status'], 'not_executed')
        self.assertEqual(model['run_id'], proposal['model_run']['run_id'])
        self.assertEqual(proposal['model_run']['model_version'], 'not-a-real-model')
        self.assertEqual(model['semantic_interpretation'], 'none')
        self.assertFalse({'kind', 'context', 'meaning', 'translation', 'confidence'} & model.keys())

    def test_external_format_report_is_explicit_and_does_not_claim_export(self):
        self.assertEqual(self.loss['schema'], 'talk2nature.interoperability-loss-report.synthetic.v1')
        self.assertEqual(self.loss['origin'], 'synthetic')
        self.assertEqual(self.loss['export_status'], 'not_performed')
        self.assertFalse(self.loss['lossless_export_supported'])
        fields = {entry['field'] for entry in self.loss['entries']}
        self.assertTrue({
            'recording_identity', 'absolute_time_and_timezone', 'frequency_bounds',
            'point_weak_box_geometry', 'labels_and_codebook',
            'reviewer_and_verification_history', 'context_provenance',
        }.issubset(fields))
        self.assertEqual(self.package['external_format_loss_report'], LOSS_REPORT.name)
        self.assertIn('Do not create an APLOSE file', self.loss['decision'])

    def test_independent_review_route_names_the_lineage_and_versioned_target(self):
        form = (ROOT / '.github/ISSUE_TEMPLATE/scientific-review.yml').read_text()
        guide = (ROOT / 'docs/ANNOTATION_LINEAGE.md').read_text()
        self.assertIn('annotation-lineage', form)
        self.assertIn('exact target software/version', form)
        self.assertIn('public [scientific methods review form]', guide)
        self.assertIn('creates a public issue and requires GitHub sign-in', guide)


if __name__ == '__main__':
    unittest.main()
