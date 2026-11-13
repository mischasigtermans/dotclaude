#!/usr/bin/env python3
import hashlib
import json
import os
import re
import sys
import tempfile
from pathlib import Path

HOME = Path.home()
SETUP = re.compile(
    re.escape(f'{HOME}/.claude/')
    + r'((CLAUDE\.md|README\.md|settings\.json)$|rules/|hooks/|skills/(?!(?:accounts|clauset|rex|synced)/))'
)
# Claude Code names a session's transcript folder after the directory it started in, so it stays put after a cd.
HOME_SESSION = re.compile(re.sub(r'[^A-Za-z0-9]', '-', str(HOME)) + r'(--claude.*)?')
SEEN = Path(tempfile.gettempdir()) / 'claude-scope-gate'
TEST = (
    "~/.claude and its skills hold reusable preferences and methods, not one project's decisions. "
    'Check the text you are adding:\n'
    '- General preferences apply in every project. Tool and framework guidance applies wherever that tool is used.\n'
    '- A product decision, client detail or project-specific correction belongs in that project or its shared guideline.\n'
    '- Local project routing belongs in private configuration. Public examples stay neutral.\n'
    'If it passes, make the same edit again. If it does not, write it where it belongs: one repo\'s rule in that repo\'s '
    'guideline (.ai/guidelines where Boost renders one, else its CLAUDE.md), a rule for a family of repos in the guideline '
    'they share. Say in one line where it went.'
)

try:
    event = json.load(sys.stdin)
    args = event.get('tool_input', {})
    path = os.path.realpath(args.get('file_path', ''))
    if SETUP.match(path):
        session = event['session_id']
        if not HOME_SESSION.fullmatch(Path(event['transcript_path']).parent.name):
            text = args.get('content') or args.get('new_string') or ''
            session += '-' + hashlib.sha1(f'{path}\n{text}'.encode()).hexdigest()
        marker = SEEN / session
        if not marker.exists():
            SEEN.mkdir(exist_ok=True)
            marker.touch()
            print(json.dumps({'hookSpecificOutput': {
                'hookEventName': 'PreToolUse',
                'permissionDecision': 'deny',
                'permissionDecisionReason': TEST,
            }}))
except Exception:
    sys.exit(0)
