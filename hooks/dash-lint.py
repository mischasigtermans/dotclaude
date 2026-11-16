#!/usr/bin/env python3
import json
import os
import re
import sys

COPY_PATH = re.compile(r'\.(md|mdx|txt|blade\.php|tsx|jsx|vue|svelte)$|/lang/')
SKIP_PATH = re.compile(r'/node_modules/|/vendor/|/\.panels/|/\.claude/(projects|plugins|panels|skills/synced)/')
PROSE_PATH = re.compile(r'\.(md|mdx|txt)$|/lang/')
DASH = re.compile(r'.{0,30}[–—].{0,30}')
DOT = re.compile(r'.{0,30}·.{0,30}')

try:
    args = json.load(sys.stdin).get('tool_input', {})
    path = os.path.realpath(args.get('file_path', ''))
    text = args.get('content') or args.get('new_string') or ''
    text = re.sub(r'```.*?```|`[^`\n]*`', '', text, flags=re.S)
    if COPY_PATH.search(path) and not SKIP_PATH.search(path):
        hits = DASH.findall(text)
        if PROSE_PATH.search(path):
            hits += DOT.findall(text)
        if hits:
            quoted = '\n'.join(f'  {h.strip()}' for h in hits[:5])
            print(json.dumps({
                'decision': 'block',
                'reason': f'{path} has em dashes, en dashes or middle dots, which Mischa never uses in copy:\n{quoted}\n'
                          'Rewrite each with a period, comma, colon or parentheses. Ranges take a hyphen, separators a pipe.',
            }))
except Exception:
    sys.exit(0)
