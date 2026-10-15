"""Exercise pinned replay before slot consistency, entirely offline."""
import copy
import hashlib
import json
from pathlib import Path
import unittest
from unittest.mock import patch

import slots

HERE = Path(__file__).resolve().parent


class SlotIntegration(unittest.TestCase):
    def setUp(self):
        self.raw = (HERE / 'plan.json').read_bytes()
        self.pin = hashlib.sha256(self.raw).hexdigest()

    def test_real_zto_replay(self):
        result = slots.review_slots(self.raw, self.pin)
        self.assertTrue(result['accepted'])
        self.assertTrue(result['evidenceChecked'])
        self.assertTrue(result['slotChecked'])
        self.assertEqual(result['slotReview']['count'], 2)

    def test_pin_before_parse_or_replay(self):
        with patch.object(slots.exact, 'inspect', side_effect=AssertionError('parsed')), \
             patch.object(slots, 'settlement_review', side_effect=AssertionError('replayed')):
            result = slots.review_slots(b'not JSON', self.pin)
        self.assertEqual(result['state'], 'plan_pin_mismatch')
        self.assertFalse(result['slotChecked'])

    def test_structure_before_evidence(self):
        raw = b'{"version":1}'
        with patch.object(slots, 'settlement_review', side_effect=AssertionError('replayed')):
            result = slots.review_slots(raw, hashlib.sha256(raw).hexdigest())
        self.assertEqual(result['state'], 'structural_review_required')
        self.assertFalse(result['evidenceChecked'])

    def test_window_excluding_actual_inclusion(self):
        plan = json.loads(self.raw)
        plan['windows'][0]['notBeforeBlock'] = 1
        plan['windows'][0]['notAfterBlock'] = 2
        raw = json.dumps(plan).encode()
        result = slots.review_slots(raw, hashlib.sha256(raw).hexdigest())
        self.assertFalse(result['accepted'])
        self.assertFalse(result['slotChecked'])

    def batch(self):
        return copy.deepcopy(slots.review_slots(self.raw, self.pin)
                             ['settlementReview']['windowReview']['batch'])

    def test_duplicate_slot(self):
        batch = self.batch()
        for field in ('block', 'transactionIndex', 'transactionCount'):
            batch['items'][1][field] = copy.deepcopy(batch['items'][0][field])
        with self.assertRaisesRegex(slots.audit.AuditError, 'duplicate block transaction slot'):
            slots.checked_slots(batch)

    def test_conflicting_counts(self):
        batch = self.batch()
        first, second = batch['items']
        second['block'] = copy.deepcopy(first['block'])
        first['transactionIndex'], second['transactionIndex'] = 0, 1
        first['transactionCount'], second['transactionCount'] = 3, 4
        with self.assertRaisesRegex(slots.audit.AuditError, 'conflicting transaction counts'):
            slots.checked_slots(batch)

    def test_hash_at_two_heights(self):
        batch = self.batch()
        batch['items'][1]['block']['hash'] = batch['items'][0]['block']['hash']
        with self.assertRaisesRegex(slots.audit.AuditError, 'conflicting heights'):
            slots.checked_slots(batch)

    def test_unaccepted_batch(self):
        with self.assertRaisesRegex(ValueError, 'settlement must pass first'):
            slots.checked_slots({'accepted': False})


if __name__ == '__main__':
    unittest.main()
