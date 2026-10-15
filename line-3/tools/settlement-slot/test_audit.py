import importlib.util
import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("slot_audit", HERE / "audit.py")
slot = importlib.util.module_from_spec(spec)
spec.loader.exec_module(slot)


def demo():
    return json.loads((HERE / "demo-report.json").read_text())


class SlotAuditTests(unittest.TestCase):
    def test_demo_accepts_unique_slots(self):
        result = slot.audit(demo())
        self.assertTrue(result["slotAudit"])
        self.assertEqual(result["uniqueBlocks"], 2)

    def test_duplicate_slot_rejected(self):
        report = demo()
        report["items"][1]["block"] = dict(report["items"][0]["block"])
        report["items"][1]["transactionIndex"] = report["items"][0]["transactionIndex"]
        with self.assertRaises(slot.AuditError):
            slot.audit(report)

    def test_conflicting_hash_for_height_rejected(self):
        report = demo()
        report["items"][1]["block"]["number"] = report["items"][0]["block"]["number"]
        with self.assertRaises(slot.AuditError):
            slot.audit(report)

    def test_index_must_fit_count(self):
        report = demo()
        report["items"][0]["transactionIndex"] = report["items"][0]["transactionCount"]
        with self.assertRaises(slot.AuditError):
            slot.audit(report)

    def test_duplicate_transaction_rejected(self):
        report = demo()
        report["items"][1]["transactionHash"] = report["items"][0]["transactionHash"]
        with self.assertRaises(slot.AuditError):
            slot.audit(report)

    def test_rejected_report_does_not_pass(self):
        report = demo()
        report["accepted"] = False
        self.assertFalse(slot.audit(report)["slotAudit"])

    def test_bad_hash_rejected(self):
        report = demo()
        report["items"][0]["block"]["hash"] = "0x0"
        with self.assertRaises(slot.AuditError):
            slot.audit(report)

    def test_duplicate_json_keys_rejected(self):
        raw = b'{"accepted":true,"accepted":true,"items":[]}'
        with self.assertRaises(slot.AuditError):
            slot.strict_json(raw)

    def test_nonfinite_json_rejected(self):
        with self.assertRaises(slot.AuditError):
            slot.strict_json(b'{"accepted":true,"items":[],"x":NaN}')


if __name__ == "__main__":
    unittest.main()
