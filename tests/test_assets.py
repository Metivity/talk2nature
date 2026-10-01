import re
import tempfile
import unittest
from pathlib import Path
from web.assets_build import copy_assets, version_html


class AssetTests(unittest.TestCase):
    def test_revision_changes_dependencies_and_document_urls_together(self):
        with tempfile.TemporaryDirectory() as d:
            source=Path(d)/'source'; source.mkdir(); target=Path(d)/'output'
            (source/'main.js').write_text("import {x} from './model.mjs'; new URL('./worker.mjs', import.meta.url);")
            (source/'model.mjs').write_text('export const x=1;')
            (source/'worker.mjs').write_text('/* worklet */')
            first=copy_assets(source,target)
            self.assertEqual(first,copy_assets(source,target))
            (source/'model.mjs').write_text('export const x=2;')
            second=copy_assets(source,target)
            self.assertNotEqual(first,second)
            self.assertEqual((target/'main.js').read_text().count('?v='+second),2)
            html=version_html('<script src="/project/assets/main.js"></script><a href="/project/app/">App</a>', '/project', second)
            self.assertIn('main.js?v='+second,html)
            self.assertIn('href="/project/app/"',html)

    def test_missing_relative_module_fails_build(self):
        with tempfile.TemporaryDirectory() as d:
            source=Path(d)/'source';source.mkdir()
            (source/'main.js').write_text("import './missing.mjs';")
            with self.assertRaisesRegex(ValueError,'Missing asset dependency'):
                copy_assets(source,Path(d)/'out')
