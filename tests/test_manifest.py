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
        self.assertEqual(result['group_counts'],{'train':6,'validation':2,'test':2})
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

    def test_optional_household_and_device_dimensions_are_transitive_and_frozen(self):
        for record in self.records:
            bird=int(record['recording_id'].split('-')[1])
            cohort=bird//2
            record['group_ids']={
                'household':[f'demo-household-{cohort:02d}'],
                'device':[f'demo-device-{cohort:02d}'],
            }
        result=split_manifest(self.records,group_dimensions=['household','device'])
        default=split_manifest(self.records)
        self.assertEqual(result['group_count'],5)
        self.assertEqual(result['group_counts'],{'train':3,'validation':1,'test':1})
        self.assertEqual(result['record_counts'],{'train':12,'validation':4,'test':4})
        self.assertEqual(result['split_policy']['additional_dimensions'],['device','household'])
        self.assertEqual(result['split_algorithm'],'connected-groups-v1')
        self.assertEqual(result['schema_version'],3)
        self.assertNotEqual(result['split_policy_sha256'],default['split_policy_sha256'])
        observed={}
        for record in self.records:
            partition=result['assignments'][record['recording_id']]
            for dimension,values in record['group_ids'].items():
                for value in values:
                    key=(dimension,value)
                    self.assertEqual(observed.setdefault(key,partition),partition)
        reordered=split_manifest(self.records,group_dimensions=['device','household'])
        self.assertEqual(result['split_policy_sha256'],reordered['split_policy_sha256'])
        self.assertEqual(result['assignments'],reordered['assignments'])

    def test_context_label_coverage_identifies_labels_missing_from_partitions(self):
        rare_individual=self.records[0]['individual_ids'][0]
        for record in self.records:
            record['context_label']='rare' if rare_individual in record['individual_ids'] else 'ordinary'
        result=split_manifest(self.records)
        coverage=result['context_label_coverage']
        self.assertEqual(coverage['declared'],['ordinary','rare'])
        rare_partition=result['assignments'][self.records[0]['recording_id']]
        for partition in ('train','validation','test'):
            observed=sorted(result['context_counts'][partition])
            self.assertEqual(coverage['by_partition'][partition]['present'],observed)
            self.assertEqual(coverage['by_partition'][partition]['missing'],
                             [label for label in coverage['declared'] if label not in observed])
            if partition==rare_partition:
                self.assertIn('rare',coverage['by_partition'][partition]['present'])
            else:
                self.assertIn('rare',coverage['by_partition'][partition]['missing'])

    def test_optional_groups_merge_across_records_and_missing_values_fail_closed(self):
        for record in self.records:
            bird=int(record['recording_id'].split('-')[1])
            record['group_ids']={'household':[f'home-{bird:02d}']}
        self.records[0]['group_ids']['household']=['bridge-a']
        self.records[2]['group_ids']['household']=['bridge-a','bridge-b']
        self.records[4]['group_ids']['household']=['bridge-b']
        result=split_manifest(self.records,group_dimensions=['household'])
        parts={result['assignments'][self.records[i]['recording_id']] for i in (0,2,4)}
        self.assertEqual(len(parts),1)
        del self.records[1]['group_ids']['household']
        with self.assertRaisesRegex(ValueError,'selected group dimension'):
            split_manifest(self.records,group_dimensions=['household'])

    def test_invalid_optional_group_ids_and_dimensions_rejected(self):
        for bad in ('unknown','N/A','', ' household'):
            records=copy.deepcopy(self.records)
            records[0]['group_ids']={'household':[bad]}
            with self.subTest(value=bad),self.assertRaises(ValueError): validate(records)
        records=copy.deepcopy(self.records)
        records[0]['group_ids']={'individual_ids':['group-a']}
        with self.assertRaisesRegex(ValueError,'dimension name'):
            validate(records)
        with self.assertRaisesRegex(ValueError,'Duplicate group dimension'):
            split_manifest(self.records,group_dimensions=['household','household'])

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
