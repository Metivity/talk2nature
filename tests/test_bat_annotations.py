import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))

from inspect_bat_annotations import summarize_paper_subset


def row(file_id, emitter, addressee, context, start=0, end=100):
    return {
        'FileID': file_id,
        'Emitter': str(emitter),
        'Addressee': str(addressee),
        'Context': str(context),
        'Start sample': str(start),
        'End sample': str(end),
    }


class BatAnnotationSubsetTests(unittest.TestCase):
    def test_reconstructs_filter_and_reports_only_aggregate_group_structure(self):
        rows = [
            row('file-a', 9001, 9002, 3, end=750_000),
            row('file-a', 9001, 0, 3, end=5),
            row('file-b', 9002, 9003, 4),
            row('file-c', 9010, 0, 2),
            row('file-d', 9020, -9021, 2),
            row('excluded-unknown', 9030, 9031, 0),
            row('excluded-landing', 9030, 9031, 8),
            row('excluded-unknown-emitter', 0, 9031, 3),
            row('excluded-ambiguous-emitter', -9040, 9031, 3),
            row('excluded-long', 9050, 9051, 3, end=750_001),
        ]

        report = summarize_paper_subset(rows)

        self.assertEqual(report['source_rows'], 10)
        self.assertEqual(report['excluded_for_context'], 2)
        self.assertEqual(report['excluded_for_emitter_identity'], 2)
        self.assertEqual(report['excluded_for_duration'], 1)
        self.assertEqual(report['retained_annotations'], 5)
        self.assertFalse(report['matches_published_count'])
        self.assertEqual(report['unique_file_ids'], 4)
        self.assertEqual(report['annotations_beyond_unique_files'], 1)
        self.assertEqual(report['files_with_multiple_annotations'], 1)
        self.assertEqual(report['files_with_multiple_contexts'], 0)
        self.assertEqual(report['rows_by_context'], {'Biting': 2, 'Feeding': 2, 'Fighting': 1})
        self.assertEqual(report['addressee_status_rows'], {'ambiguous': 1, 'identified': 2, 'unknown': 2})
        self.assertEqual(report['unique_positive_participants_across_roles'], 5)
        self.assertEqual(report['unique_distinct_participant_pairs'], 2)

        groups = report['grouping_feasibility']
        self.assertEqual(groups['source_file_only']['connected_groups'], 4)
        self.assertEqual(groups['source_file_plus_emitter']['connected_groups'], 4)
        self.assertEqual(groups['source_file_plus_all_known_participants']['connected_groups'], 3)
        self.assertEqual(groups['source_file_plus_all_known_participants']['largest_group_annotations'], 3)
        self.assertEqual(groups['source_file_plus_all_known_participants']['largest_group_files'], 2)
        self.assertEqual(groups['source_file_plus_all_known_participants']['largest_group_known_animals'], 3)

        serialized = json.dumps(report)
        for identifier in ('file-a', 'file-b', 'file-c', 'file-d', '9001', '9002', '9003', '9010', '9020', '9021'):
            self.assertNotIn(identifier, serialized)


if __name__ == '__main__':
    unittest.main()
