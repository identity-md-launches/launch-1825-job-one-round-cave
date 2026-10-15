#!/usr/bin/env python3
"""Pack verified public Ethereum RPC snapshots into one offline capsule."""
import argparse
import base64
import hashlib
import hmac
import json
from pathlib import Path
import re
import runpy
import sys
import types

HERE = Path(__file__).resolve().parents[1]
BOUNDED = runpy.run_path(str(HERE / 'bounded-rpc-snapshot' / 'snapshot.py'))
SAFE = runpy.run_path(str(HERE / 'safe-snapshot-files' / 'safe_files.py'))
MAX_SNAPSHOT = BOUNDED['MAX_RESPONSE'] + BOUNDED['MAX_REQUEST']
MAX_ITEMS = 8
MAX_CAPSULE = 8_500_000
NAME = re.compile(r'[A-Za-z0-9][A-Za-z0-9._-]{0,119}\.json\Z')
HEX = re.compile(r'[0-9a-f]{64}\Z')


class CapsuleError(ValueError):
    pass


def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise CapsuleError('duplicate JSON key: ' + key)
        result[key] = value
    return result


def parse(raw):
    try:
        return json.loads(raw, object_pairs_hook=unique_pairs,
                          parse_constant=lambda x: (_ for _ in ()).throw(
                              CapsuleError('invalid JSON number: ' + x)))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CapsuleError('invalid JSON: ' + str(exc)) from exc


def validate_snapshot(raw):
    if type(raw) is not bytes or not 1 <= len(raw) <= MAX_SNAPSHOT:
        raise CapsuleError('snapshot bytes exceed bounded format')
    original = BOUNDED['verify_snapshot']
    isolated = dict(original.__globals__)
    isolated['SAFE_FILES'] = {'read_bytes': lambda path, limit: raw}
    verifier = types.FunctionType(original.__code__, isolated)
    try:
        return verifier('capsule-memory')
    except (BOUNDED['SnapshotError'], OSError, ValueError) as exc:
        raise CapsuleError('invalid RPC snapshot: ' + str(exc)) from exc


def pack(paths):
    if not 1 <= len(paths) <= MAX_ITEMS:
        raise CapsuleError(f'choose between 1 and {MAX_ITEMS} snapshots')
    items = []
    names = set()
    for path in paths:
        SAFE['parts'](path)
        name = path.rsplit('/', 1)[-1]
        if not NAME.fullmatch(name) or name in names:
            raise CapsuleError('snapshot names must be unique simple .json filenames')
        names.add(name)
        raw = SAFE['read_bytes'](path, MAX_SNAPSHOT)
        validate_snapshot(raw)
        items.append({'name': name, 'bytes': len(raw),
                      'sha256': hashlib.sha256(raw).hexdigest(),
                      'snapshot_base64': base64.b64encode(raw).decode('ascii')})
    return {'schema': 'line1-snapshot-capsule-v1', 'items': items}


def review(value):
    if type(value) is not dict or set(value) != {'schema', 'items'}:
        raise CapsuleError('capsule must contain only schema and items')
    if value['schema'] != 'line1-snapshot-capsule-v1':
        raise CapsuleError('unsupported capsule schema')
    items = value['items']
    if type(items) is not list or not 1 <= len(items) <= MAX_ITEMS:
        raise CapsuleError(f'capsule must contain between 1 and {MAX_ITEMS} items')
    names = set()
    results = []
    for item in items:
        if type(item) is not dict or set(item) != {
                'name', 'bytes', 'sha256', 'snapshot_base64'}:
            raise CapsuleError('invalid capsule item fields')
        name, size, digest, encoded = (item['name'], item['bytes'],
                                       item['sha256'], item['snapshot_base64'])
        if type(name) is not str or not NAME.fullmatch(name) or name in names:
            raise CapsuleError('invalid or duplicate snapshot name')
        names.add(name)
        if type(size) is not int or not 1 <= size <= MAX_SNAPSHOT:
            raise CapsuleError('invalid snapshot byte count')
        if type(digest) is not str or not HEX.fullmatch(digest):
            raise CapsuleError('invalid snapshot SHA-256')
        if type(encoded) is not str or len(encoded) > ((MAX_SNAPSHOT + 2) // 3) * 4:
            raise CapsuleError('encoded snapshot exceeds limit')
        try:
            raw = base64.b64decode(encoded, validate=True)
        except (ValueError, base64.binascii.Error) as exc:
            raise CapsuleError('invalid snapshot base64') from exc
        if len(raw) != size:
            raise CapsuleError('snapshot byte count mismatch')
        actual = hashlib.sha256(raw).hexdigest()
        if not hmac.compare_digest(actual, digest):
            raise CapsuleError('snapshot SHA-256 mismatch')
        snapshot = validate_snapshot(raw)
        results.append({'name': name, 'bytes': size, 'sha256': actual,
                        'captured_at_utc': snapshot['captured_at_utc'],
                        'rpc_url': snapshot['rpc_url'],
                        'request': snapshot['request'],
                        'response_sha256': snapshot['response_sha256']})
    return {'accepted': True, 'schema': value['schema'], 'count': len(results),
            'snapshots': results,
            'meaning': 'Each embedded snapshot passes the inherited bounded RPC verifier and its exact-byte checksum matches the capsule manifest. Retain the capsule SHA-256 separately to detect replacement of the whole capsule.'}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    create = commands.add_parser('pack', help='verify and embed snapshots')
    create.add_argument('--output', required=True, help='new relative workspace JSON path')
    create.add_argument('snapshots', nargs='+')
    verify = commands.add_parser('verify', help='check a capsule offline')
    verify.add_argument('capsule')
    args = parser.parse_args(argv)
    try:
        if args.command == 'pack':
            SAFE['parts'](args.output)
            capsule = pack(args.snapshots)
            rendered = (json.dumps(capsule, sort_keys=True, separators=(',', ':'),
                                   ensure_ascii=True, allow_nan=False) + '\n').encode('ascii')
            if len(rendered) > MAX_CAPSULE:
                raise CapsuleError('complete capsule exceeds byte limit')
            SAFE['write_bytes'](args.output, rendered, MAX_CAPSULE)
            result = review(capsule)
            result['capsule_sha256'] = hashlib.sha256(rendered).hexdigest()
            result['capsule_bytes'] = len(rendered)
        else:
            SAFE['parts'](args.capsule)
            raw = SAFE['read_bytes'](args.capsule, MAX_CAPSULE)
            result = review(parse(raw))
            result['capsule_sha256'] = hashlib.sha256(raw).hexdigest()
            result['capsule_bytes'] = len(raw)
        print(json.dumps(result, ensure_ascii=True, separators=(',', ':'), allow_nan=False))
        return 0
    except (CapsuleError, BOUNDED['SnapshotError'], SAFE['FileBoundaryError'],
            OSError, ValueError, TypeError, OverflowError, RecursionError) as exc:
        print('snapshot-capsule: ' + str(exc)[:1000], file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
