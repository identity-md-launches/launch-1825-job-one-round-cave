"""Read back this round's deliverables; report byte checks and visual limits."""
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess


def jpeg_dimensions(data):
    assert data[:2] == b'\xff\xd8' and data[-2:] == b'\xff\xd9'
    offset = 2
    while offset < len(data):
        assert data[offset] == 255
        marker = data[offset + 1]
        size = int.from_bytes(data[offset + 2:offset + 4], 'big')
        assert size >= 2
        if marker == 192:
            return (int.from_bytes(data[offset + 7:offset + 9], 'big'),
                    int.from_bytes(data[offset + 5:offset + 7], 'big'))
        offset += size + 2
    raise ValueError('no baseline JPEG frame')


def main():
    spec = importlib.util.spec_from_file_location('delivery_image_bytes', 'line-2/image_bytes.py')
    image = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(image)
    paths = ['artifacts/line-2/wall-v19.png', 'artifacts/line-2/wall.png']
    walls = [Path(name).read_bytes() for name in paths]
    assert walls[0] == walls[1]
    width, height, pixels = image.read_png(walls[0])
    assert (width, height) == (1254, 1254) and len(pixels) == width * height * 3
    preview = Path('dist/line-2/39.jpg').read_bytes()
    assert jpeg_dimensions(preview) == (512, 512) and len(preview) < 100000
    record = json.loads(Path('dist/line-2/39.json').read_text())
    assert set(record) == {'name', 'image', 'attributes'}
    assert record['image'] == 'https://api.imd.fun/artifacts/' + hashlib.sha256(walls[0]).hexdigest()
    attrs = record['attributes']
    assert [a['trait_type'] for a in attrs] == ['Cave', 'Wall', 'Number', 'Left behind', 'Meaning', 'One thing']
    assert all(set(a) == {'trait_type', 'value'} for a in attrs)
    assert [a['value'] for a in attrs[:3]] == ['Water', 'Line 2', 39]
    assert type(attrs[2]['value']) is int
    assert len(list(Path('dist/line-2').glob('*.json'))) == 39
    # Compare only assigned task data with its repository baseline.
    goal = subprocess.check_output(['git', 'show', 'HEAD:line-2/GOAL.md'])
    assert Path('line-2/GOAL.md').read_bytes() == goal
    subprocess.run(['git', 'diff', '--exit-code', '--', 'line-2/GOAL.md', 'dist/line-2'], check=True)
    tracked = subprocess.check_output(['git', 'ls-files', '--', *paths]).decode().strip()
    assert not tracked, 'named wall outputs must remain untracked'
    files = list(Path('line-2/tools/exact-contract').glob('*'))
    files += [Path('line-2/WALL-39.md'), Path('line-2/wall-review-39.json'),
              Path('dist/line-2/39.json'), Path('dist/line-2/39.jpg'),
              Path('line-2/check_delivery_39.py')]
    for path in files:
        raw = path.read_bytes()
        assert len(raw) < 100000, str(path)
        if path.suffix == '.json':
            json.loads(raw)
        elif path.suffix == '.py':
            ast.parse(raw, filename=str(path))
        elif path.suffix == '.md':
            assert raw.decode('utf-8').strip()
    results = json.loads(Path('line-2/tools/exact-contract/validation.json').read_text())
    assert results['passed'] and all(c['exit'] == c['expected_exit'] for c in results['commands'])
    review = json.loads(Path('line-2/wall-review-39.json').read_text())
    assert review['wall']['sha256'] == hashlib.sha256(walls[0]).hexdigest()
    assert review['unmet_visual_requirements'] and review['pixel_identity_claim'] is False
    report = {'byte_and_format_checks_passed': True, 'wall_dimensions': [width, height],
              'wall_format': 'PNG', 'jpeg_dimensions': [512, 512], 'jpeg_format': 'JPEG',
              'png_sha256': hashlib.sha256(walls[0]).hexdigest(), 'record_number': 39,
              'goal_bytes_unchanged': True, 'older_records_unchanged': True,
              'named_wall_outputs_untracked': True, 'tool_command_trials': len(results['commands']),
              'regression_tests_per_suite': results['tests_per_suite'],
              'all_visual_requirements_met': False,
              'unmet_visual_requirements': review['unmet_visual_requirements'],
              'meaning': 'Local checks only, not independent certification.'}
    Path('line-2/check-results-39.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
