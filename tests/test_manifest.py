import copy
import hashlib
import json
import random
import unittest
from pathlib import Path
from talk2nature.manifest import split_manifest, validate


class ManifestTests(unittest.TestCase):
    def setUp(self):
        self.records=json.loads((Path(__file__).resolve().parents[1]/'examples/recordings.synthetic.json').read_text())

    def test_identity_session_and_source_never_cross_partitions(self):
        result=split_manifest(self.records)
        observed={}
        for r in self.records:
            keys=[('individual',v) for v in r['individual_ids']]+[('session',r['session_id']),('source',r['source_sha256'])]
            for key in keys:
                partition=result['assignments'][r['recording_id']]
                self.assertEqual(observed.setdefault(key,partition),partition)
        self.assertTrue(all(result['record_counts'].values()))

    def test_transitive_relationships_are_kept_together(self):
        self.records[0]['individual_ids']=['bridge-a']
        self.records[2]['individual_ids']=['bridge-a','bridge-b']
        self.records[4]['individual_ids']=['bridge-b']
        self.records[6]['source_sha256']=self.records[4]['source_sha256']
        result=split_manifest(self.records)
        parts={result['assignments'][self.records[i]['recording_id']] for i in (0,2,4,6)}
        self.assertEqual(len(parts),1)

    def test_reordering_does_not_change_split_or_provenance(self):
        first=split_manifest(self.records)
        random.Random(71).shuffle(self.records)
        second=split_manifest(self.records)
        self.assertEqual(first['assignments'],second['assignments'])
        self.assertEqual(first['manifest_sha256'],second['manifest_sha256'])

    def test_one_animal_is_not_a_valid_individual_holdout(self):
        for r in self.records: r['individual_ids']=['one-parrot']
        with self.assertRaisesRegex(ValueError,'Only 1 independent'): split_manifest(self.records)

    def test_unresolved_rights_and_audio_derived_labels_rejected(self):
        for field,value in [('license','unknown'),('consent_status','pending'),('label_source','model_prediction'),('sensitive_location',True),('source_sha256','not-a-hash'),('individual_ids',['unknown']),('recorded_at','2026-09-30T10:00:00')]:
            records=copy.deepcopy(self.records); records[0][field]=value
            with self.subTest(field=field),self.assertRaises(ValueError): validate(records)

    def test_duplicate_ids_and_mixed_synthetic_data_rejected(self):
        records=copy.deepcopy(self.records); records[1]['recording_id']=records[0]['recording_id']
        with self.assertRaisesRegex(ValueError,'Duplicate'): validate(records)
        records=copy.deepcopy(self.records); records[0]['synthetic']=False
        with self.assertRaisesRegex(ValueError,'mix synthetic'): validate(records)

    def test_changed_metadata_changes_manifest_fingerprint(self):
        first=split_manifest(self.records)
        self.records[0]['context_label']='unknown'
        second=split_manifest(self.records)
        self.assertNotEqual(first['manifest_sha256'],second['manifest_sha256'])
        self.assertEqual(first['assignments'],second['assignments'])


if __name__=='__main__': unittest.main()
