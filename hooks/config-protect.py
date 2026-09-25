#!/usr/bin/env python3
import json
import re
import sys

LINT_CONFIG = re.compile(r'(^|/)(pint\.json|phpstan(\.dist)?\.neon(\.dist)?|\.prettierrc[^/]*|prettier\.config\.[cm]?[jt]s|eslint\.config\.[cm]?[jt]s|\.eslintrc[^/]*)$')

try:
    path = json.load(sys.stdin).get('tool_input', {}).get('file_path', '')
    if LINT_CONFIG.search(path):
        print(json.dumps({'hookSpecificOutput': {
            'hookEventName': 'PreToolUse',
            'permissionDecision': 'deny',
            'permissionDecisionReason': f'{path} is linter or formatter config. Fix the code, not the config. If the config itself is wrong, ask Mischa.',
        }}))
except Exception:
    sys.exit(0)
