import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from talk2nature.annotations import report, validate

FIXTURE = Path(__file__).resolve().parents[1] / 'examples/annotations.synthetic.json'


class AnnotationTests(unittest.TestCase):
    def setUp(self): self.document = json.loads(FIXTURE.read_text())

    def test_shared_browser_fixture_report(self):
        result = report(self.document)
        self.assertEqual(result['event_count'], 2)
        self.assertEqual(result['annotated_union_seconds'], 2)
        self.assertEqual(result['context_observed_union_seconds'], 0)
        self.assertEqual(result['context_counts'], {'unknown': 2})
        self.assertEqual(result['declared_origin'], 'synthetic')

    def test_overlap_is_counted_once_and_touching_intervals_are_not_overlap(self):
        self.document['events'][1].update(start_seconds=1.5, end_seconds=3)
        result = report(self.document)
        self.assertEqual(result['annotated_union_seconds'], 2)
        self.assertEqual(result['overlapping_pair_count'], 1)
        self.document['events'][1]['start_seconds'] = 2
        self.assertEqual(report(self.document)['overlapping_pair_count'], 0)

    def test_context_requires_declared_independent_observation(self):
        self.document['events'][0]['context'] = 'feeding'
        with self.assertRaises(ValueError): validate(self.document)
        self.document['events'][0]['context_source'] = 'direct observation'
        self.assertEqual(report(self.document)['context_observed_union_seconds'], 1)

    def test_reject_bad_types_ranges_duplicates_and_nan(self):
        for patch in ({'id': True}, {'start_seconds': -1}, {'end_seconds': float('nan')}, {'end_seconds': 9}, {'context': 'happy'}, {'notes': None}):
            document = copy.deepcopy(self.document); document['events'][0].update(patch)
            with self.subTest(patch=patch), self.assertRaises(ValueError): validate(document)
        self.document['events'].append(dict(self.document['events'][0]))
        with self.assertRaises(ValueError): validate(self.document)

    def test_empty_labels_are_valid_but_warn(self):
        self.document['events'] = []
        result = report(self.document)
        self.assertEqual(result['annotated_union_seconds'], 0)
        self.assertIn('No events have been annotated.', result['warnings'])

    def test_cli_produces_report_and_refuses_overwriting_input_or_output(self):
        with tempfile.TemporaryDirectory() as d:
            output = Path(d) / 'report.json'
            command = [sys.executable, '-m', 'talk2nature.annotations', str(FIXTURE), '--output', str(output)]
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(output.read_text())['event_count'], 2)
            self.assertEqual(subprocess.run(command, capture_output=True).returncode, 2)
            command[-1] = str(FIXTURE)
            self.assertEqual(subprocess.run(command, capture_output=True).returncode, 2)
