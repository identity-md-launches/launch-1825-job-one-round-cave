"""Check shared slot integration here and detached, without network."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
SCRATCH = ROOT / 'test/scratch/slots-detached'
PIN = 'be5ee9b0eefa06067695aac1caaaa5b1dabb8a505d3025f3a9ed447e4c525cb5'


def main():
    shutil.copytree(ROOT / 'shared/window-settlement', SCRATCH / 'shared/window-settlement',
                    dirs_exist_ok=True)
    commands = [
        (ROOT, ['shared/window-settlement/test_slots.py'], 0),
        (ROOT, ['shared/window-settlement/slots.py', 'shared/window-settlement/plan.json', '--sha256', PIN], 0),
        (SCRATCH, ['shared/window-settlement/test_slots.py'], 0),
        (SCRATCH, ['shared/window-settlement/slots.py', 'shared/window-settlement/plan.json', '--sha256', PIN], 0),
        (ROOT, ['shared/window-settlement/slots.py', 'shared/window-settlement/plan.json', '--sha256', 'a'*64], 1),
        (ROOT, ['shared/window-settlement/slots.py', '../plan.json', '--sha256', PIN], 2),
    ]
    results = []
    for cwd, args, expected in commands:
        r = subprocess.run([sys.executable, '-B', *args], cwd=cwd,
                           capture_output=True, text=True, timeout=30)
        passed = r.returncode == expected
        if 'test_slots.py' not in args[0]:
            report = json.loads(r.stdout)
            passed = passed and report['accepted'] is (expected == 0)
        results.append(dict(command=args, detached=cwd == SCRATCH, expectedExit=expected,
                            exitCode=r.returncode, passed=passed,
                            stdoutSha256=hashlib.sha256(r.stdout.encode()).hexdigest(),
                            stdoutBytes=len(r.stdout.encode()), stderr=r.stderr))
    (ROOT / 'gathering/round-checks-19.json').write_text(json.dumps(results, indent=2)+'\n')
    print(json.dumps({'passed': all(r['passed'] for r in results), 'trials': len(results)}))
    return 0 if all(r['passed'] for r in results) else 1


if __name__ == '__main__':
    sys.exit(main())
