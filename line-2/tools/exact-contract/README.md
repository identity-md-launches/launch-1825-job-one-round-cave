# Exact-decimal JSON contract checker

Check JSON deliverables offline without rounding decimal number literals through
binary floating point. This self-contained Python 3.10+ standard-library tool
supports the existing line-2 structural contract language. It reports every
independent structural violation using escaped JSON Pointer paths. Existing
tools and their numeric semantics are unchanged.

One command from the repository root shows a passing exact boundary:

```sh
python3 -B line-2/tools/exact-contract/check.py line-2/tools/exact-contract/precision.contract.json line-2/tools/exact-contract/at-limit.json
```

Observed: exit 0, `valid: true`, `complete: true`. Replace `at-limit.json` with
`over-limit.json`: exit 1, `valid: false`, and a `maximum` violation at `/amount`.
The maximum is `9007199254740992.0`; the rejected amount is
`9007199254740993.0`. The inherited binary64 checker accepts this latter case
because the two floating-point values round together. These small fixtures
demonstrate numeric semantics; they are not payments or live token balances.

For a retained real ZTO-related manifest already present in this repository:

```sh
python3 -B line-2/tools/exact-contract/check.py line-2/tools/field-relations/window.contract.json line-2/tools/field-relations/window-plan.json
```

Observed: exit 0, valid and complete. Only the manifest's JSON structure is
checked. Evidence paths inside the document are data and are never opened.
This is not a new chain observation, settlement decision, or amount check.
The first command and all tests work with this folder alone.

## Numeric and contract rules

Integer literals remain Python integers. Decimal-point or exponent literals
become `decimal.Decimal` directly from their original tokens, without binary64
conversion or arithmetic rounding. Bounds, enum equality (including nested
objects/arrays), and `uniqueItems` use exact numeric comparisons. `1`, `1.0`
and `1e0` compare numerically equal, but only `1` satisfies type `integer`.
Booleans never compare as numbers. Negative zero equals zero. Decimal numbers
beyond the binary64 range are supported within the limits below. Changing the
Decimal context's precision does not change these comparisons.

Supported rules: `type`, `enum`; object `properties`, `required`,
`additionalProperties`; array `items`, `prefixItems`, `minItems`, `maxItems`,
`uniqueItems`; string `minLength`, `maxLength`, `pattern`; numeric `minimum`,
`maximum`. Unknown, incompatible, or contradictory rules refuse. Strings do
not become numbers. Integer means an integer JSON literal, not an integral
decimal. This is an explicit subset, not full JSON Schema. No cross-field
comparison, source byte ranges, or automatic repair is added here.

## File boundary, pins, and results

Inputs must be visible relative workspace paths to regular files, each at most
1,000,000 bytes. Every path component is traversed using no-follow directory
descriptors; symlinks, hidden components, parent traversal, absolute paths,
directories and special files refuse. POSIX `O_NOFOLLOW`/`O_DIRECTORY` are
required. A growing file cannot defeat the byte cap. Hard links and mounted
directories are not excluded; this is not an operating-system sandbox.

Both source byte counts and SHA-256 values are reported. Optional
`--contract-sha256 HEX` and `--document-sha256 HEX` check independently retained
lowercase SHA-256 pins before either JSON input is interpreted. Inputs are
captured once per lexical path. Hashes do not authenticate authors or facts;
retain expectations separately. Files can change after capture.

Exit 0 means valid, 1 means structural violations, 2 means an input, contract,
pin, or complete-output error. Require both exit 0 and `valid: true`.
`complete: true` alone also accompanies rejected documents. Diagnostics contain
no Decimal objects, so their JSON serialization loses no numeric precision.
The program writes only stdout and makes no network, environment, wallet,
secret, configuration, signing, or transaction access.

## Checks and limits

```sh
python3 -B line-2/tools/exact-contract/test_check.py
```

All 22 regression tests passed: precise neighboring bounds, exact enums and
uniqueness, mixed integer/decimal equality, boolean separation, integer-literal
typing, negative zero, extreme finite values, low Decimal precision, escaped
pointers, prefix items, source hashes, pins before parsing, one capture per
path, exit codes, malformed/duplicate/nonfinite JSON, token/exponent bounds,
and symlink/path/size refusal. A test initially passed an absolute scratch path;
it was corrected to exercise the documented relative-path interface. All
fixtures are synthetic, local, and temporary under `test/scratch/`.

Numeric tokens are limited to 4096 characters, with decimal exponent magnitude
at most 1,000,000. Complete output is capped at 1,000,000 UTF-8 bytes; overflow
returns exit 2 with `complete: false`, never a truncated acceptance report.
Deep inputs can refuse on Python recursion limits. Trusted regular expressions
and quadratic uniqueness checks are not a CPU sandbox. This tool checks
structure, not semantic truth or business approval. No coin is needed.

Implementation adapts the unchanged inherited `json-contract/check.py` engine
and `bounded-contract/check.py` reader into ordinary local code. Provenance
hashes and recorded command outcomes are in `validation.json`. Nothing needs
installation or network access.
