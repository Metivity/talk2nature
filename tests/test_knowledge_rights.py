import json
import tempfile
import unittest
from pathlib import Path

from web.build import build


class KnowledgeRightsTests(unittest.TestCase):
    def test_evidence_map_explains_rights_labels_and_computes_catalog_caveat(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            build(root, 'https://fixture.github.io/talk2nature', True,
                  'https://github.com/Metivity/talk2nature')
            page = (root / 'research/map/index.html').read_text()
            resources = json.loads(
                (Path(__file__).parents[1] / 'research/resources.json').read_text()
            )['resources']
            flagged = sum(
                any(resource['rights'][field] in {'unresolved', 'not_admitted'}
                    for field in ('research_use', 'commercial_use', 'redistribution'))
                for resource in resources
            )
            self.assertIn(f'{flagged} of {len(resources)} resources', page)
            self.assertIn('This is a catalog status, not a legal clearance.', page)
            self.assertIn('A possible use only if the listed conditions are met.', page)
            self.assertIn('The reviewed evidence did not settle permission for this use.', page)
            self.assertIn('Talk2Nature has not admitted this component for this use.', page)
            self.assertIn('Acquisition and analysis have separate project gates.', page)
            self.assertIn('assets/knowledge-rights.css', page)


if __name__ == '__main__':
    unittest.main()
