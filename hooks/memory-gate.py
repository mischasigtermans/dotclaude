#!/usr/bin/env python3
import json
import os
import re
import sys
from pathlib import Path

MEMORY_FILE = re.compile(r'/\.claude/projects/[^/]+/memory/[^/]+\.md$')
TYPE = re.compile(r'^\s*type:\s*(\w+)', re.M)
STATUS = re.compile(
    r'\b(uncommitted|not (yet )?(committed|pushed|merged|deployed)|next steps?|in progress|in flight|'
    r'still open|wip|nog open|nog niet|volgende stap)\b',
    re.I,
)


def project_root(cwd):
    path = Path(cwd)
    for candidate in (path, *path.parents):
        if (candidate / '.git').exists():
            return candidate
    return path


def deny(reason):
    print(json.dumps({'hookSpecificOutput': {
        'hookEventName': 'PreToolUse',
        'permissionDecision': 'deny',
        'permissionDecisionReason': reason,
    }}))


try:
    event = json.load(sys.stdin)
    args = event.get('tool_input', {})
    path = os.path.realpath(args.get('file_path', ''))
    if MEMORY_FILE.search(path) and not path.endswith('/MEMORY.md'):
        text = args.get('content') or args.get('new_string') or ''
        head = text if TYPE.search(text) else (Path(path).read_text() if Path(path).exists() else '')
        kind = TYPE.search(head)
        kind = kind.group(1) if kind else ''
        if kind == 'feedback':
            root = project_root(event.get('cwd', '.'))
            repo = (f'{root}/.ai/guidelines/<topic>.md, then `php artisan boost:update`'
                    if (root / '.ai/guidelines').is_dir() else f'{root}/CLAUDE.md')
            deny('Rules never go in memory. Write this one where it belongs. '
                 f'For this repo: {repo}. For a family of repos: the guideline they share. '
                 'For how I work in every project, naming none: ~/.claude/CLAUDE.md, ~/.claude/rules/ or a skill. '
                 'Say in one line where it went.')
        elif kind == 'project' and STATUS.search(text):
            deny(f'Memory holds facts, not status ("{STATUS.search(text).group(0)}"). '
                 'Work in flight goes in a Solo todo or scratchpad, what happened is in git. '
                 'Keep only what stays true and the code cannot tell a future session.')
except Exception:
    sys.exit(0)
