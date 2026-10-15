#!/usr/bin/env python3
"""Replay a pinned window plan before checking the verified transaction slots."""
import argparse
import hashlib
import json
import sys

from review import module, review as settlement_review, window, CONTRACT, render

exact = module('slot_exact_contract', 'vendor/exact_contract.py')
audit = module('slot_audit', 'vendor/slot_audit.py')
CONTRACT_BYTES = json.dumps(CONTRACT, separators=(',', ':')).encode('ascii')
FIELDS = ('accepted', 'transactionHash', 'block', 'transactionIndex', 'transactionCount')
LIMITATIONS = ('Historical provider observations, not consensus, freshness, payment or authorization. '
    'Unique slots do not prove settlement; this command replays pinned evidence first. '
    'Retain plan and evidence hashes independently. No cross-run ledger or deduplication.')


def checked_slots(batch):
    """Project verifier-produced rows; never accept an uploaded acceptance report."""
    if batch.get('accepted') is not True:
        raise ValueError('settlement must pass first')
    projected = {'accepted': True,
                 'items': [{field: row[field] for field in FIELDS} for row in batch['items']]}
    result = audit.audit(projected)
    # A single block has one transaction count. Different heights also cannot
    # share one hash. The inherited slot audit does not test these assertions.
    counts, heights = {}, {}
    for row in projected['items']:
        anchor = row['block']
        number, block_hash = anchor['number'], audit.hash32(anchor['hash'])
        if number in counts and counts[number] != row['transactionCount']:
            raise audit.AuditError('block has conflicting transaction counts')
        if block_hash in heights and heights[block_hash] != number:
            raise audit.AuditError('block hash has conflicting heights')
        counts[number] = row['transactionCount']
        heights[block_hash] = number
    return result


def review_slots(raw, expected_sha256):
    window.b.k.pin(expected_sha256)
    if type(raw) is not bytes or len(raw) > window.b.k.LIMIT:
        raise ValueError('bounded exact plan bytes required')
    actual = hashlib.sha256(raw).hexdigest()
    result = dict(accepted=False, state='plan_pin_mismatch', actualPlanSha256=actual,
                  expectedPlanSha256=expected_sha256, evidenceChecked=False,
                  slotChecked=False, limitations=LIMITATIONS)
    if actual != expected_sha256:
        return result
    # Share Line 2's exact decimal parser and structural diagnostics. Pins are
    # checked before either parsing or evidence reads; raw is captured once.
    structure = exact.inspect(CONTRACT_BYTES, raw)
    result['structure'] = structure
    if structure['valid'] is not True:
        result['state'] = 'structural_review_required'
        render(result)
        return result
    settlement = settlement_review(raw, expected_sha256)
    result.update(settlementReview=settlement, state=settlement['state'],
                  evidenceChecked=settlement['evidenceChecked'])
    if settlement['accepted'] is not True:
        render(result)
        return result
    result['slotChecked'] = True
    try:
        slots = checked_slots(settlement['windowReview']['batch'])
        result['slotReview'] = slots
        result.update(accepted=slots['slotAudit'] is True,
                      state='settlement_window_slots_match' if slots['slotAudit'] else
                            'slot_review_required')
    except audit.AuditError as exc:
        result.update(state='slot_review_required', slotReview={
            'slotAudit': False, 'reason': str(exc)})
    render(result)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('plan', help='visible workspace-relative plan path')
    parser.add_argument('--sha256', required=True, help='independently retained exact plan hash')
    args = parser.parse_args(argv)
    try:
        window.b.k.pin(args.sha256)
        # Use the descriptor-relative capped no-follow reader, never audit.load.
        raw = window.b.k.load_bytes(args.plan)
        result = review_slots(raw, args.sha256)
        sys.stdout.write(render(result))
        return 0 if result['accepted'] else 2 if result['state'] == 'input_error' else 1
    except (ValueError, TypeError, KeyError, OSError, RecursionError, window.Error):
        print(json.dumps(dict(accepted=False, state='input_error', evidenceChecked=False,
                              slotChecked=False, reason='Invalid bounded plan, pin, evidence or report')))
        return 2


if __name__ == '__main__':
    sys.exit(main())
