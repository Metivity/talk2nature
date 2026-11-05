import tempfile
import unittest
from pathlib import Path

from scripts.check_site import PageParser, check_site
from web.build import build


class FilePickerContractTests(unittest.TestCase):
    def test_generated_file_inputs_have_labels_hints_and_selection_feedback(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            build(root,'https://fixture.github.io/talk2nature',True)
            check_site(root)
            inputs=[]
            for path in root.rglob('*.html'):
                page=PageParser()
                page.feed(path.read_text())
                inputs.extend((path,control) for control in page.file_inputs)

        self.assertEqual(len(inputs),10)
        for path,control in inputs:
            with self.subTest(page=path.relative_to(root),input_id=control['id']):
                picker=control['picker']
                self.assertIsNotNone(picker)
                self.assertEqual(picker['for'],control['id'])
                self.assertTrue(control['accept'])
                self.assertTrue(picker['hint'])
                self.assertTrue(picker['selection'])
                self.assertTrue(''.join(picker['text']).strip())

    def test_site_check_rejects_a_bare_file_input(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            build(root,'https://fixture.github.io/talk2nature',True)
            page=root/'tools'/'listen'/'index.html'
            page.write_text(page.read_text().replace('class="file-picker"','class="file-picker-missing"',1))
            with self.assertRaisesRegex(ValueError,'file input must have a labeled format hint'):
                check_site(root)


if __name__=='__main__':
    unittest.main()
