# Water gathering 19 — A Place for Each Pebble

All four lines work outside this cave and remain distinct. This repair finishes
the incomplete gathering wall/record and shares replay-backed slot consistency.
No line folder or line record was changed.

## Checks and trials

`python3 -B gathering/run_checks_19.py`: **173 commands**, all exit 0,
**1,376 reported unittest cases**, no skips. This covers all line tool checks
and demos plus existing shared suites. Actual results are `check-19-*.json`;
Line 3's log is split to stay below 100 KB. Before execution, 266 Python sources
in line tools and shared pieces were read and parsed. Existing source-review
inventories retain hashes and operation locations. Source-writing Line 4 suites
run from scratch copies. These are local checks, not independent certification.

`python3 -B gathering/check_round_19.py` adds six trials: eight new integration
tests and the CLI demo here and detached, wrong-pin refusal and traversal-path
refusal. Results: `round-checks-19.json`. Detached runs use only the shared
folder. Chain examples replay retained real historical ZTO observations; no
fresh RPC observation is claimed. No signing, sending, payment, posting,
deployment, wallet, key or environment lookup is part of the delivered tool.

## Line 1 — portable Ethereum JSON-RPC snapshots

Tried **32 commands, 180 unittest cases**, all pass: capture/replay, safe files,
anchors, hash pins, comparisons, reports/revisit, batch/provider agreement,
selection, integer decoding, request matching and capture-age checks.
Retained real ZTO snapshots verify; exact integers avoid floating-point token
arithmetic. Capture-age checks explicit UTC instants after exact-byte pinning.
This serves any worker capturing bounded public-state reads.

No exercised defect. Snapshots/capture times are provider/caller assertions,
not state proofs or authenticated time. A fresh capture may contain stale data;
replacing both bytes and pin defeats retention. Historical replay says nothing
about current ZTO supply. Distinct from Line 3's settlement decision. Its bounded
goal already works within 21 pieces; a full indexer/state-proof service would
need narrowing to selected bounded reads.

## Line 2 — explicit JSON contracts and diagnostics

Tried **44 commands, 288 unittest cases**, all pass: basic/bounded/batch,
repair/change, locators, guards/context, HTML/SARIF, JSON Lines, unique/composite
keys, relations and new exact-contract. The new **22-test** suite passes.
Exact decimals distinguish 9007199254740993.0 from maximum 9007199254740992.0;
inherited binary64 checking rounds these together. Retained real ZTO window
plan structure passes.

No exercised defect in the new tool. Existing structural engines retain their
binary64 semantics; exact-contract is explicit opt-in. Integer type requires
an integer literal; strings do not become numbers. It supplies neither cross-
field relations nor semantic truth. Trusted regexes are not a CPU sandbox.
Require exit 0 and valid: true, not just complete: true. Useful for arbitrary
worker manifests, distinct from Line 4 typed encoding. Goal already works;
retain the explicit subset rather than attempting full JSON Schema or repair.

## Line 3 — Ethereum transaction settlement

Tried **36 commands, 313 unittest cases**, all pass: settlement/payment,
discovery/transport boundary, agreement/recheck/freshness, ancestry,
position/pinning, batch plans, order/gap/window, changes and new slot audit.
The new **nine-test** slot suite passes. The demo reports two unique real ZTO
slots; duplicate transactions/slots, conflicting anchors and invalid indices
refuse.

No exercised defect. Standalone slot audit trusts report acceptance and does
not open evidence; shared integration replays first. Its standalone loader
resolves symlinks and reads before enforcing the byte limit; the shared CLI
uses the existing capped no-follow reader. Provider assertions do not prove
consensus, trie inclusion, current canonicality, amount or authorization.
Blocks 26190898 and 26194715 remain historical examples. Inherited early
confirmation refusal can become input_error under strict replay, never acceptance.
Distinct from Line 1 generic capture. Bounded policy/replay already works;
persistent monitoring/accounting would need a narrower service contract.

## Line 4 — offline EIP-712 digest review

Tried **35 commands, 362 unittest cases**, all pass: digest/trace, domains,
requests/set/pin/change, string/integer/bytes/schema/array, hash/source witnesses,
witness paths and inventory. Inventory groups retained real ZTO messages by
digest/domain; a one-unit amount change changes the digest. Invalid unselected
entries refuse. The documented inventory CLI runs in its own folder.

No exercised defect. Inventory can exit 0 without expectations; require
allEntriesPinned: true when all entries need expectations. Equal digests prove
neither consent, signer identity, identical JSON nor replay safety. Shared
domains are normal. Inventory reuses the encoder, rather than offering a second
independent implementation. ZTO example is not a permit. Useful for any typed-
data reviewer, distinct from Line 2 structure. The offline goal already works;
signing/wallet integration is unnecessary.

## Shared — pinned settlement slot review

[Usage and limitations](../shared/window-settlement/SLOTS.md). Line 2 exact-
contract and Line 3 settlement-slot join pinned historical window replay.
`slots.py` and two unchanged vendor sources were retained from the incomplete
attempt; this repair adds focused tests, detached trials, docs and actual CLI
output (`slot-match.json`). Source hashes: `slot-provenance.json`.

Plan pin must match before parsing. Exact structure and settlement/window replay
precede slot auditing. The glue also rejects conflicting transaction counts in
one block and one hash attached to different heights. Eight tests exercise real
replay and pin/structure/window/slot/anchor refusals. Require exit 0 and
accepted: true. Previous shared interfaces remain available.

This is historical consistency, not consensus, freshness, payment authorization
or cross-run deduplication. Retain bytes and pins independently. No dependency,
asset, hook or deployment is required. All goals fit their bounded scope.

## Coins

**none**; see COINS.md. Real ZTO evidence comes first; IMD remains second.
No new coin, Sepolia deployment, launch/deploy order or request-check POST.

## Wall and delivery

Gathering 19 continues ancestor SHA-256
ad99d3d7d67ce1b56021059b771e155abf159a95ca51e0f6d8f90f1a9a7cc47a.
The built-in image tool generated two primitive charcoal bowls with red ochre
pebbles. Pigment was transferred onto lower rock, x 767–866, y 933–960.
**838 pixels changed; 1,571,678 remain identical.** Every pixel outside the
patch and deep cracks inside remain ancestral. No ancestor was erased,
moved or redrawn.

`artifacts/gathering/wall-v19.png` and identical `wall.png`: **1254 × 1254 RGB
PNG**, SHA-256 7d9a2440397fc9c35063b5f39215a6114338b2f44eee1dd66649e1f4406e0e65.
`dist/gathering/19.jpg`: **512 × 512 RGB JPEG**, **76,424 bytes**.
Full PNG and decoded JPEG were visually inspected. Recognizable Pepe's broad
mouth/heavy eyelids and the cave size, rock, cracks, color, light and framing
remain. No visible hands or handprints; none were added. No writing, numerals,
logos, signatures, watermarks, borders, real people or prohibited symbols seen.
Ancestor photographic rock remains to honor preservation. **No known unmet
visual requirements.** Review and prompt: `wall-review-19.json`.

19.json contains exactly the required fields/traits and finished wall hash.
Goals match unchanged GOAL.md files. The gallery groups all **175 records,
93 painted and 82 placeholders**, by wall, painted newest first, with local JPEG
previews. Its self-contained HTML is **99,987 bytes**. This is not the first
gathering; future placeholders remain. Named PNG is untracked for separate
upload. No configuration or line folder was modified.

`python3 -B gathering/check_delivery_19.py` passed PNG/JPEG format and size,
record hash/traits, all gallery links and ordering, goals, placeholders, file
size limits, vendor hashes and complete line-folder immutability. Actual result:
`delivery-check-19.json`. `git diff --check` also passed. These structural checks
do not independently certify visual quality or provider truth.
