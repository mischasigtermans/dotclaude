#!/usr/bin/env python3
import json
import re
import sys
import tempfile
from pathlib import Path

UI_PATH = re.compile(r'\.(blade\.php|html|tsx|jsx|vue|svelte|css)$')
NOT_UI = re.compile(r'/\.ai/|/vendor/|/node_modules/')
RULE = Path.home() / '.claude/rules/ui.md'
SEEN = Path(tempfile.gettempdir()) / 'claude-ui-gate'


def rule_loaded(transcript_path):
    with open(transcript_path) as f:
        for line in f:
            entry = json.loads(line)
            content = entry.get('message', {}).get('content')
            if entry.get('type') != 'assistant' or not isinstance(content, list):
                continue
            for c in content:
                if c.get('type') == 'tool_use' and c.get('name') == 'Read' and UI_PATH.search(c.get('input', {}).get('file_path', '')):
                    return True
    return False


try:
    event = json.load(sys.stdin)
    path = event.get('tool_input', {}).get('file_path', '')
    marker = SEEN / event['session_id']
    # rules/ui.md is path-scoped and only loads on a Read of a UI file; reading through Bash skips it.
    if UI_PATH.search(path) and not NOT_UI.search(path) and not marker.exists() and not rule_loaded(event['transcript_path']):
        SEEN.mkdir(exist_ok=True)
        marker.touch()
        rule = re.sub(r'^---\n.*?\n---\n', '', RULE.read_text(), flags=re.S).strip()
        print(json.dumps({'hookSpecificOutput': {
            'hookEventName': 'PreToolUse',
            'permissionDecision': 'deny',
            'permissionDecisionReason': f'Before this UI edit, apply these rules, then make the edit again:\n\n{rule}',
        }}))
except Exception:
    sys.exit(0)
