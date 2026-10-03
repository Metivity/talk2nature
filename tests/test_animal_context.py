import json
from pathlib import Path
import unittest
from talk2nature.animal_context import GROUPS, validate_animal
from talk2nature.annotations import validate, report


class AnimalContextTests(unittest.TestCase):
    def fixture(self):
        return json.loads((Path(__file__).resolve().parents[1] / 'examples/annotations.synthetic.json').read_text())

    def test_optional_legacy_and_all_groups(self):
        self.assertIsNone(report(self.fixture())['declared_animal_context'])
        for group in GROUPS:
            context = {'group': group, 'species': 'תוכי · 🦜', 'basis': 'observer-declared'}
            doc = self.fixture(); doc['animal_context'] = context
            self.assertEqual(report(doc)['declared_animal_context'], context)
            self.assertEqual(report(doc)['declared_origin'], 'synthetic')

    def test_rejects_malformed_or_asserted_automatic_identity(self):
        good = {'group': 'parrot', 'species': '', 'basis': 'observer-declared'}
        for context in (None, [], {}, {**good, 'group': []}, {**good, 'group': 'dragon'},
                        {**good, 'basis': 'AI-verified'}, {**good, 'species': 'x'*81},
                        {**good, 'species': 'a\nb'}, {**good, 'species': ' leading'},
                        {**good, 'confidence': 1}, {**good, 'species': '🦜'*41}):
            doc = self.fixture(); doc['animal_context'] = context
            with self.subTest(context=context), self.assertRaises(ValueError): validate(doc)
        validate_animal({**good, 'species': '🦜'*40})
