# Settlement slot audit

`settlement-slot` is a small offline, standard-library check for an already
accepted Ethereum settlement batch. It verifies that every accepted item has a
valid transaction index, that no two items claim the same `(block, index)`
slot, and that one block number never appears with conflicting block hashes.
It opens no RPC endpoint, wallet, key, transaction, or referenced evidence.

From the repository root, run the bundled example:

```sh
python3 -B line-3/tools/settlement-slot/audit.py --demo
```

The demo exits 0 with `slotAudit: true`. For a worker-owned report, use:

```sh
python3 -B line-3/tools/settlement-slot/audit.py --report path/to/accepted-batch.json
```

Exit 0 means the report is accepted and its slots are internally unique; exit
1 means a review is required; exit 2 means bounded input is invalid. This is a
consistency check, not consensus proof, a reorg proof, freshness, payment
authorization, or evidence of settlement by itself. Retain the batch and its
independent pin separately and run the settlement verifier first.

Tried locally: the demo and the focused tests pass; duplicate slots,
conflicting block anchors, out-of-range indices, rejected reports, duplicate
JSON keys, and malformed hashes are refused.
