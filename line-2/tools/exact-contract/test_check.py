"""Offline regressions for exact numeric structural validation."""
import contextlib
from decimal import Decimal, localcontext
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('exact_checker', Path(__file__).with_name('check.py'))
check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check)


class ExactTests(unittest.TestCase):
    def inspect(self, contract, document):
        return check.inspect(contract.encode(), document.encode())

    def test_precision_above_binary64(self):
        result = self.inspect('{"type":"number","maximum":9007199254740992.0}',
                              '9007199254740993.0')
        self.assertFalse(result['valid'])
        self.assertEqual(result['errors'][0]['rule'], 'maximum')

    def test_decimal_below_minimum(self):
        self.assertFalse(self.inspect('{"type":"number","minimum":0.100000000000000001}',
                                      '0.1')['valid'])

    def test_equal_spellings(self):
        for value in ('1', '1.0', '1e0', '10e-1'):
            self.assertTrue(self.inspect('{"type":"number","enum":[1.00]}', value)['valid'])

    def test_integer_literal_distinction(self):
        self.assertTrue(self.inspect('{"type":"integer"}', '1')['valid'])
        for value in ('1.0', '1e0', 'true'):
            self.assertFalse(self.inspect('{"type":"integer"}', value)['valid'])

    def test_number_rejects_bool(self):
        self.assertFalse(self.inspect('{"type":"number"}', 'true')['valid'])

    def test_nested_enum_numeric_equality(self):
        c = '{"type":"object","enum":[{"a":[1.0,true]}]}'
        self.assertTrue(self.inspect(c, '{"a":[1,true]}')['valid'])
        self.assertFalse(self.inspect(c, '{"a":[1,1]}')['valid'])

    def test_unique_preserves_exact_neighbors(self):
        c = '{"type":"array","uniqueItems":true}'
        self.assertTrue(self.inspect(c, '[9007199254740992.0,9007199254740993.0]')['valid'])
        r = self.inspect(c, '[1,1.0,true]')
        self.assertEqual([e['path'] for e in r['errors']], ['/1'])

    def test_negative_zero(self):
        self.assertTrue(self.inspect('{"type":"number","enum":[0]}', '-0.0')['valid'])

    def test_large_small_finite(self):
        for token in ('1e99999', '-1e99999', '1e-99999'):
            self.assertTrue(self.inspect('{"type":"number"}', token)['valid'])

    def test_decimal_context_does_not_round_comparisons(self):
        with localcontext() as ctx:
            ctx.prec = 2
            self.assertFalse(self.inspect('{"type":"number","maximum":1.000000000000001}',
                                          '1.000000000000002')['valid'])

    def test_contradictory_bounds_exact(self):
        with self.assertRaises(ValueError):
            self.inspect('{"type":"number","minimum":1.000000000000002,"maximum":1.000000000000001}', '1')

    def test_limits_require_integer_literals(self):
        with self.assertRaises(ValueError):
            self.inspect('{"type":"array","minItems":1.0}', '[]')

    def test_multiple_pointer_violations(self):
        c = '{"type":"object","required":["a/b"],"properties":{"a/b":{"type":"number"},"x~y":{"type":"number","minimum":0.1}},"additionalProperties":false}'
        r = self.inspect(c, '{"x~y":0.09,"extra":0}')
        self.assertEqual([e['path'] for e in r['errors']], ['/a~1b', '/x~0y', '/extra'])

    def test_prefix_items(self):
        c = '{"type":"array","prefixItems":[{"type":"integer"}],"items":{"type":"number","maximum":0.1}}'
        self.assertFalse(self.inspect(c, '[1,0.100000000000000001]')['valid'])

    def test_reject_ambiguous_json(self):
        for raw in (b'{"a":1,"a":2}', b'NaN', b'Infinity', b'1 2', b'\xff'):
            with self.assertRaises((ValueError, UnicodeError)):
                check.decode(raw)

    def test_numeric_resource_limits(self):
        for raw in (b'1e1000001', b'1e-1000001', b'1' * 4097,
                    b'0.' + b'0' * 4095 + b'1'):
            with self.assertRaises(ValueError):
                check.decode(raw)

    def test_exact_source_identities(self):
        c, d = b'{"type":"number"}', b'1.000\r\n'
        result = check.inspect(c, d)
        self.assertEqual(result['sources']['document'],
                         {'sha256': hashlib.sha256(d).hexdigest(), 'bytes': len(d)})

    def cli(self, files, args):
        with patch.object(check, 'read_bytes', side_effect=lambda name: files[name]) as reader:
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                status = check.main(args)
        return status, json.loads(out.getvalue()), reader

    def test_cli_statuses(self):
        c = b'{"type":"number","maximum":0.1}'
        for raw, expected in ((b'0.1', 0), (b'0.10000000000000001', 1), (b'NaN', 2)):
            status, result, _ = self.cli({'c': c, 'd': raw}, ['c', 'd'])
            self.assertEqual(status, expected)
            self.assertEqual(result['valid'], expected == 0)
            self.assertEqual(result['complete'], expected != 2)

    def test_pins_before_parse(self):
        status, result, _ = self.cli({'c': b'bad', 'd': b'bad'},
                                    ['c', 'd', '--document-sha256', '0' * 64])
        self.assertEqual(status, 2)
        self.assertIn('document SHA-256 mismatch', result['error'])

    def test_same_path_captured_once(self):
        _, _, reader = self.cli({'c': b'{"type":"object"}'}, ['c', 'c'])
        reader.assert_called_once_with('c')

    def test_correct_pin(self):
        raw = b'1.0'
        status, _, _ = self.cli({'c': b'{"type":"number"}', 'd': raw},
                                ['c', 'd', '--document-sha256', hashlib.sha256(raw).hexdigest()])
        self.assertEqual(status, 0)

    def test_safe_reader(self):
        Path('test/scratch').mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir='test/scratch') as tmp:
            base = Path(tmp).relative_to(Path.cwd()) if Path(tmp).is_absolute() else Path(tmp)
            regular = base / 'data.json'
            regular.write_bytes(b'1.0')
            self.assertEqual(check.read_bytes(str(regular)), b'1.0')
            (base / 'link.json').symlink_to('data.json')
            with self.assertRaises(OSError):
                check.read_bytes(str(base / 'link.json'))
            (base / 'dirlink').symlink_to('.', target_is_directory=True)
            with self.assertRaises(OSError):
                check.read_bytes(str(base / 'dirlink/data.json'))
            with self.assertRaises(ValueError):
                check.read_bytes(str(regular), limit=2)
        for name in ('/absolute', '../parent', '.hidden', 'a//b'):
            with self.assertRaises(ValueError):
                check.read_bytes(name)


if __name__ == '__main__':
    unittest.main()
