#!/usr/bin/env python3
"""Audit uniqueness and anchor consistency of an accepted settlement batch."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

MAX_BYTES = 100_000
MAX_ITEMS = 32
HASH = re.compile(r"0x[0-9a-fA-F]{64}\Z")


class AuditError(ValueError):
    pass


def strict_json(raw):
    if type(raw) is not bytes or len(raw) > MAX_BYTES:
        raise AuditError("bounded UTF-8 JSON required")

    def pairs(items):
        out = {}
        for key, value in items:
            if key in out:
                raise AuditError("duplicate JSON key")
            out[key] = value
        return out

    def constant(value):
        raise AuditError("nonfinite JSON value")

    try:
        return json.loads(raw.decode("utf-8"), object_pairs_hook=pairs,
                          parse_constant=constant)
    except (UnicodeError, json.JSONDecodeError, RecursionError) as exc:
        raise AuditError("invalid JSON") from exc


def hash32(value):
    if not isinstance(value, str) or not HASH.fullmatch(value):
        raise AuditError("expected 32-byte hash")
    return value.lower()


def unsigned(value, label):
    if type(value) is not int or value < 0:
        raise AuditError(label + " must be an unsigned integer")
    return value


def audit(report):
    if (not isinstance(report, dict) or set(report) != {"accepted", "items"}
            or report["accepted"] is not True
            or not isinstance(report["items"], list)
            or not 1 <= len(report["items"]) <= MAX_ITEMS):
        return {"slotAudit": False, "state": "report_not_accepted"}

    seen_tx = set()
    seen_slots = set()
    blocks = {}
    rows = []
    try:
        for item in report["items"]:
            if (not isinstance(item, dict)
                    or set(item) != {"accepted", "transactionHash", "block",
                                      "transactionIndex", "transactionCount"}
                    or item["accepted"] is not True):
                raise AuditError("every item must be accepted with exact fields")
            tx = hash32(item["transactionHash"])
            block = item["block"]
            if not isinstance(block, dict) or set(block) != {"number", "hash"}:
                raise AuditError("exact block anchor required")
            number = unsigned(block["number"], "block number")
            block_hash = hash32(block["hash"])
            index = unsigned(item["transactionIndex"], "transaction index")
            count = item["transactionCount"]
            if type(count) is not int or not 1 <= count <= 2**32 - 1:
                raise AuditError("transaction count out of range")
            if index >= count:
                raise AuditError("transaction index outside block transaction count")
            if tx in seen_tx:
                raise AuditError("duplicate transaction")
            seen_tx.add(tx)
            if number in blocks and blocks[number] != block_hash:
                raise AuditError("block number has conflicting hashes")
            blocks[number] = block_hash
            slot = (number, block_hash, index)
            if slot in seen_slots:
                raise AuditError("duplicate block transaction slot")
            seen_slots.add(slot)
            rows.append({"transactionHash": tx, "blockNumber": number,
                         "blockHash": block_hash, "transactionIndex": index})
    except (TypeError, KeyError) as exc:
        raise AuditError("malformed batch item") from exc
    return {"slotAudit": True, "state": "unique_slots_and_anchors",
            "count": len(rows), "uniqueBlocks": len(blocks), "items": rows,
            "evidenceChecked": False,
            "limitations": "This checks report consistency only; it does not open evidence, "
                           "prove consensus or freshness, or authorize payment."}


def load(path):
    if (not isinstance(path, str) or not path or path.startswith("/")
            or "\\" in path or any(not p or p.startswith(".") for p in path.split("/"))):
        raise AuditError("visible workspace-relative report path required")
    root = Path.cwd().resolve()
    candidate = (root / path).resolve()
    if root not in candidate.parents or not candidate.is_file():
        raise AuditError("report must be a regular file inside the workspace")
    return candidate.read_bytes()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--demo", action="store_true")
    source.add_argument("--report")
    args = parser.parse_args(argv)
    try:
        path = (Path(__file__).resolve().parent / "demo-report.json").relative_to(Path.cwd()) \
            if args.demo else args.report
        raw = load(str(path))
        result = audit(strict_json(raw))
        result["reportSha256"] = hashlib.sha256(raw).hexdigest()
        if args.demo:
            result["demoNote"] = "Two retained real ZTO settlement slots; historical consistency example."
        encoded = json.dumps(result, indent=2, ensure_ascii=True, allow_nan=False) + "\n"
        if len(encoded.encode("ascii")) > MAX_BYTES:
            raise AuditError("report exceeds output limit")
        print(encoded, end="")
        return 0 if result["slotAudit"] else 1
    except (AuditError, OSError, ValueError, TypeError, RecursionError):
        print(json.dumps({"slotAudit": False, "state": "input_error"}))
        return 2


if __name__ == "__main__":
    sys.exit(main())
