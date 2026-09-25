#!/usr/bin/env python3
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

STATE = Path(tempfile.gettempdir()) / 'claude-php-format'


def state_file(event):
    STATE.mkdir(exist_ok=True)
    return STATE / f"{event['session_id']}.txt"


def record(event):
    path = event.get('tool_input', {}).get('file_path', '')
    if path.endswith('.php') and not path.endswith('.blade.php') and '/vendor/' not in path:
        with open(state_file(event), 'a') as f:
            f.write(path + '\n')


def project_root(path):
    for parent in Path(path).parents:
        if (parent / 'vendor/bin/pint').exists():
            return parent
    return None


def analysed_paths(config):
    # PHPStan analyses any file it is handed, so the hook narrows to the config's own `paths:` list.
    paths, inside = [], False
    for line in config.read_text().splitlines():
        stripped = line.strip()
        if stripped == 'paths:':
            inside = True
        elif inside and stripped.startswith('- '):
            paths.append((config.parent / stripped[2:].strip().strip('\'"')).resolve())
        elif inside and stripped and not stripped.startswith('#'):
            break
    return paths


def in_scope(path, paths):
    resolved = Path(path).resolve()
    return not paths or any(resolved == p or p in resolved.parents for p in paths)


def run(cmd, cwd, timeout):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)


def verify(event):
    pending = state_file(event)
    if not pending.exists():
        return
    paths = sorted({p for p in pending.read_text().splitlines() if p and os.path.exists(p)})
    pending.unlink()

    projects = {}
    for path in paths:
        root = project_root(path)
        if root:
            projects.setdefault(root, []).append(path)

    errors = []
    for root, files in projects.items():
        run(['vendor/bin/pint', *files], root, 60)

        configs = [root / c for c in ('phpstan.neon', 'phpstan.neon.dist', 'phpstan.dist.neon') if (root / c).exists()]
        analysed = [f for f in files if in_scope(f, analysed_paths(configs[0]))] if configs else []
        if (root / 'vendor/bin/phpstan').exists() and analysed:
            result = run(['vendor/bin/phpstan', 'analyse', '--no-progress', '--error-format=raw', '--memory-limit=1G', *analysed], root, 150)
            if result.returncode != 0:
                errors.append(f'{root.name}:\n{result.stdout.strip()[:3000]}')

    if errors and not event.get('stop_hook_active'):
        print(json.dumps({
            'decision': 'block',
            'reason': 'PHPStan fails on files you changed. Fix these before you finish:\n\n' + '\n\n'.join(errors),
        }))


try:
    event = json.load(sys.stdin)
    if event.get('hook_event_name') == 'PostToolUse':
        record(event)
    elif event.get('hook_event_name') == 'Stop':
        verify(event)
except Exception:
    sys.exit(0)
