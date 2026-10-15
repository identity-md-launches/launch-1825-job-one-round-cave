# Pinned settlement slot review

Gathering 19 joins Line 2's exact-decimal structural checker with Line 3's
slot audit and this folder's pinned historical settlement replay. The two
unchanged vendor sources and their hashes are in `slot-provenance.json`.
Copy the whole folder to use it independently; Python standard library only.

From the repository root:

```sh
python3 -B shared/window-settlement/slots.py shared/window-settlement/plan.json --sha256 be5ee9b0eefa06067695aac1caaaa5b1dabb8a505d3025f3a9ed447e4c525cb5
```

Observed: exit 0, `accepted: true`, `settlement_window_slots_match`, two unique
historical real ZTO slots. Complete output is `slot-match.json`. For another
plan, supply its path and an independently retained exact-byte SHA-256.
The bundled self-check demonstrates mechanics, not policy approval.

The pin must match before parsing or evidence reads. Exact structural
validation precedes settlement and inclusive window replay. Only rows produced
by that replay reach the slot audit; an uploaded acceptance report cannot
bypass replay. Duplicate transactions, overlapping block transaction slots,
conflicting anchors, inconsistent transaction counts within a block and a
block hash assigned to different heights refuse. Earlier tools stay unchanged.

Require exit 0 and `accepted: true`. Exit 1 means mismatch or review required;
exit 2 means invalid input or processing failure. No partial acceptance is
emitted. Plans use the existing capped, workspace-relative, no-follow reader;
complete reports are limited to 100,000 bytes.

```sh
python3 -B shared/window-settlement/test_slots.py
```

Eight tests pass: retained real ZTO replay, pin-before-parse, structure-before-
evidence, excluded inclusion, duplicate slots, conflicting counts, conflicting
heights and rejected batches. Tests also pass with only this folder copied
into scratch. Deliberately mutated reports test refusal, not live observations.

This is internal consistency of historical provider observations, not consensus,
trie inclusion, current canonicality, freshness, payment amount or authorization.
There is no persistent ledger or deduplication across runs. Retain plan and
evidence hashes independently. No new coin, installation, keys, environment
reads, signing, sending or deployment is required.
