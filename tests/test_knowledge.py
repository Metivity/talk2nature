import unittest
from copy import deepcopy
from talk2nature.knowledge import catalog_graph
from admin.catalog import read_catalog


class KnowledgeTests(unittest.TestCase):
    def test_catalog_is_deterministic_and_closed(self):
        entries = read_catalog()
        graph = catalog_graph(entries)
        self.assertEqual(graph, catalog_graph(list(reversed(entries))))
        self.assertEqual(graph['visibility'], 'public_metadata')
        self.assertTrue(graph['edges'])
        nodes = {n['id'] for n in graph['nodes']}
        self.assertTrue(all(e['from'] in nodes and e['to'] in nodes for e in graph['edges']))
        self.assertTrue(all(e['relation'] == 'cites' for e in graph['edges']))

    def test_changed_record_changes_version_and_private_fields_do_not_leak(self):
        entry = {'key':'source:1','kind':'source','title':'A source','payload':{'title':'A source','url':'https://example.org/paper'}}
        before = catalog_graph([entry])
        changed = deepcopy(entry); changed['payload']['private_note'] = 'DO NOT PUBLISH'
        after = catalog_graph([changed])
        self.assertNotEqual(before['nodes'][0]['id'],after['nodes'][0]['id'])
        self.assertNotIn('DO NOT PUBLISH', str(after))
        with self.assertRaises(ValueError): catalog_graph([entry,entry])
        with self.assertRaises(ValueError): catalog_graph([{'key':'note:a','kind':'note','title':'N','payload':{'source_ids':[99]}}])
