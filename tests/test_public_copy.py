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
            public_html = '\n'.join(path.read_text() for path in root.rglob('*.html'))
            self.assertIn('Curiosity, held with care.', home)
            self.assertIn('Start with a<br><em>small observation.</em>', companion)
            self.assertNotIn('Less scrolling.', public_html)
            self.assertNotIn('More noticing.', public_html)


if __name__ == '__main__':
    unittest.main()
