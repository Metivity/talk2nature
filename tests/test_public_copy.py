import tempfile
import unittest
from pathlib import Path

from web.build import build


class PublicCopyTests(unittest.TestCase):
    def test_internal_feedback_phrase_is_not_rendered_for_visitors(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            build(root, 'https://fixture.github.io/talk2nature', True)
            home = (root / 'index.html').read_text()
            companion = (root / 'app' / 'index.html').read_text()
            community = (root / 'community' / 'index.html').read_text()
            public_html = '\n'.join(path.read_text() for path in root.rglob('*.html'))
            self.assertIn('Curiosity, held with care.', home)
            self.assertIn('<title>Open-source animal communication research and bioacoustic tools · Talk2Nature</title>', home)
            self.assertIn('An open-source project for animal communication research, bioacoustics and tools that help people document nature.', home)
            self.assertIn('Find a way to help', home)
            self.assertIn('Start with a<br><em>small observation.</em>', companion)
            self.assertIn('Try an example', community)
            self.assertIn('Question a claim', community)
            self.assertIn('Suggest a source', community)
            self.assertNotIn('Less scrolling.', public_html)
            self.assertNotIn('More noticing.', public_html)


if __name__ == '__main__':
    unittest.main()
