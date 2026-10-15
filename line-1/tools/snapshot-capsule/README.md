# Snapshot capsule

This standard-library Python tool packs several already saved Ethereum RPC
snapshots into one portable JSON file. Packing first checks every snapshot with
Line 1's bounded RPC verifier. The offline verifier checks each embedded byte
count, SHA-256, request, response and response checksum, then reports the
verified requests together. It does not make network calls.

Run from the repository root:

```sh
python3 -B line-1/tools/snapshot-capsule/capsule.py verify line-1/tools/snapshot-capsule/demo-capsule.json
```

Tried here: that command accepted the 28,417-byte demo capsule with two saved
real public-read captures: ZTO `totalSupply()` (`eth_call`) and a finalized
Ethereum block (`eth_getBlockByNumber`). Both passed the inherited verifier.
The demo reuses captures already in the workspace; it made no fresh chain
request.

To create a capsule from 1–8 visible workspace snapshots:

```sh
python3 -B line-1/tools/snapshot-capsule/capsule.py pack --output test/scratch/reads.json line-1/tools/snapshot-integer/live-zto.json line-1/tools/snapshot-select/live-block.json
```

The capsule holds exact source bytes and a hash for each item. Keep the printed
`capsule_sha256` somewhere separate if you need to detect replacement of the
whole capsule: its internal hashes cannot authenticate a replaced manifest.
These checks do not establish provider identity, timestamp authenticity, block
freshness, or Ethereum consensus. The tool has no external dependencies, wallet,
key, signature, transaction or coin requirement.
