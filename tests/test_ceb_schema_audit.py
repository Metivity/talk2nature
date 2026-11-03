import unittest

from research.ceb_schema_audit import summarize_schema


class CebSchemaAuditTests(unittest.TestCase):
    def schema(self):
        return {
            'name': 'ceb-schema',
            'applies_to': ['train_soundscape.csv'],
            'primary_unit': 'one annotated sound event per row',
            'fields': [
                {'name': 'filepath', 'type': 'string', 'description':
                 'Anonymized relative path of the form <subset>_project_<NNN>/audio_<NNNNNN>.flac.'},
                {'name': 'start_time', 'type': 'number', 'description': 'Event start time.'},
            ],
        }

    def test_summary_preserves_file_grouping_without_claiming_site_independence(self):
        result = summarize_schema(self.schema())
        self.assertEqual(result['field_count'], 2)
        self.assertIn('filepath', result['field_names'])
        self.assertIn('same exact filepath', result['split_guidance'])
        self.assertIn('does not establish independent site', result['split_guidance'])
        self.assertIn('not verified negative intervals', result['bird_presence_readiness'])
        self.assertFalse(result['schema_file']['training_admitted'])

    def test_unexpected_row_unit_fails_closed(self):
        schema = self.schema()
        schema['primary_unit'] = 'one recording per row'
        with self.assertRaisesRegex(ValueError, 'Unexpected CEB row unit'):
            summarize_schema(schema)

    def test_missing_recording_path_fails_closed(self):
        schema = self.schema()
        schema['fields'][0]['name'] = 'filename'
        with self.assertRaisesRegex(ValueError, 'documented anonymized recording-path'):
            summarize_schema(schema)


if __name__ == '__main__':
    unittest.main()
