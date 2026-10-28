import json
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path
from talk2nature.knowledge import catalog_graph
from admin.catalog import read_catalog
from web.knowledge_build import build_knowledge


class KnowledgeTests(unittest.TestCase):
    def test_catalog_is_deterministic_and_closed(self):
        entries = read_catalog()
        graph = catalog_graph(entries)
        self.assertEqual(graph, catalog_graph(list(reversed(entries))))
        self.assertEqual(graph['visibility'], 'public_metadata')
        self.assertTrue(graph['edges'])
        nodes = {n['id'] for n in graph['nodes']}
        self.assertTrue(all(e['from'] in nodes and e['to'] in nodes for e in graph['edges']))
        self.assertTrue(all(e['relation'] in {'cites','cataloged_from'} for e in graph['edges']))
        nodes = {n['key']:n for n in graph['nodes']}
        resource = nodes['resource:animal-audio-identity-site-leakage-audit']
        source = nodes['source:172']
        self.assertIn({'from':resource['id'],'relation':'cataloged_from','to':source['id'],
                       'basis':'Explicit source_ids in this resource; target is the catalog version at graph build time.'},graph['edges'])
        resource_nodes={node['id'] for node in graph['nodes'] if node['kind']=='resource'}
        linked_resources={edge['from'] for edge in graph['edges'] if edge['relation']=='cataloged_from'}
        self.assertEqual(resource_nodes,linked_resources)

    def test_cataloged_resource_cannot_link_to_missing_source(self):
        entries = [
            {'key':'source:1','kind':'source','title':'Source','payload':{'title':'Source','url':'https://example.org/source'}},
            {'key':'resource:code','kind':'resource','title':'Code','payload':{'title':'Code','source_ids':[2]}},
        ]
        with self.assertRaisesRegex(ValueError,'missing source'):
            catalog_graph(entries)

    def test_public_notes_and_resources_must_have_a_source_edge(self):
        source={'key':'source:1','kind':'source','title':'Source','payload':{'title':'Source','url':'https://example.org/source'}}
        for kind in ('note','resource'):
            entry={'key':f'{kind}:orphan','kind':kind,'title':'Orphan','payload':{'title':'Orphan','source_ids':[]}}
            with self.subTest(kind=kind), self.assertRaisesRegex(ValueError,'at least one source'):
                catalog_graph([source,entry])
            historical=catalog_graph([source,entry],require_source_edges=False)
            self.assertEqual(len(historical['nodes']),2)

    def test_public_catalog_rejects_dangling_resource_source_reference(self):
        repo = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root/'content').mkdir()
            (root/'research').mkdir()
            for relative in ('content/sources.json','content/research.json','research/resources.json'):
                data = json.loads((repo/relative).read_text())
                if relative == 'research/resources.json':
                    next(row for row in data['resources'] if row['id']=='animal-audio-identity-site-leakage-audit')['source_ids'] = [999999]
                (root/relative).write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError,'Resource cites a missing or invalid source'):
                read_catalog(root)

    def test_public_catalog_rejects_source_free_resource(self):
        repo=Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary)
            (root/'content').mkdir()
            (root/'research').mkdir()
            for relative in ('content/sources.json','content/research.json','research/resources.json'):
                data=json.loads((repo/relative).read_text())
                if relative=='research/resources.json':
                    next(row for row in data['resources'] if row['id']=='animal-audio-identity-site-leakage-audit')['source_ids']=[]
                (root/relative).write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError,'Resource must reference at least one source'):
                read_catalog(root)

    def test_changed_record_changes_version_and_private_fields_do_not_leak(self):
        entry = {'key':'source:1','kind':'source','title':'A source','payload':{'title':'A source','url':'https://example.org/paper'}}
        before = catalog_graph([entry])
        changed = deepcopy(entry); changed['payload']['private_note'] = 'DO NOT PUBLISH'
        after = catalog_graph([changed])
        self.assertNotEqual(before['nodes'][0]['id'],after['nodes'][0]['id'])
        self.assertNotIn('DO NOT PUBLISH', str(after))
        with self.assertRaises(ValueError): catalog_graph([entry,entry])
        with self.assertRaises(ValueError): catalog_graph([{'key':'note:a','kind':'note','title':'N','payload':{'source_ids':[99]}}])

    def test_public_map_renders_notes_resources_and_source_citations(self):
        repo = Path(__file__).resolve().parents[1]
        sources = json.loads((repo/'content/sources.json').read_text())
        notes = json.loads((repo/'content/research.json').read_text())
        with tempfile.TemporaryDirectory() as temporary:
            pages = []
            build_knowledge(repo, Path(temporary), '/talk2nature',
                            lambda *args, **kwargs: pages.append((args, kwargs)), notes, sources)
            body = pages[0][0][3]
            records = json.loads((repo/'research/resources.json').read_text())['resources']
            expected = len(notes) + len(records) + len(sources)
            self.assertEqual(body.count('class="graph-record"'), expected)
            self.assertIn(f'{len(notes)} research notes', body)
            self.assertIn(f'{len(records)} linked research resources', body)
            self.assertIn(f'{len(sources)} original source citations', body)
            self.assertIn('id="evidence-bird-call-syntax"', body)
            self.assertIn('id="resource-anuraset-data"', body)
            self.assertIn('id="source-1"', body)
            self.assertIn('id="graph-kind-filter"', body)
            self.assertIn('Public metadata only. No recordings, participant observations or private records.', body)
            graph = json.loads((Path(temporary)/'research/map/catalog.json').read_text())
            self.assertEqual(len(graph['nodes']), expected)
