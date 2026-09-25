#!/usr/bin/env python3
import json
import re
import shlex
import sys

TRAILER = re.compile(r'co-authored-by|signed-off-by', re.I)
TAG_READ_FLAGS = {'-l', '--list', '--contains', '--no-contains', '--merged', '--no-merged', '--points-at', '--sort', '-n'}


def segments(command):
    lexer = shlex.shlex(command, posix=True, punctuation_chars=';&|')
    lexer.whitespace_split = True
    segment = []
    for token in lexer:
        if token and set(token) <= set(';&|'):
            yield segment
            segment = []
        else:
            segment.append(token)
    yield segment


def git_violation(args):
    options, i = [], 0
    while i < len(args) and args[i].startswith('-'):
        if args[i] in ('-C', '-c'):
            options.append(args[i + 1] if i + 1 < len(args) else '')
            i += 2
        else:
            i += 1
    if any(o.startswith('core.hooksPath') for o in options):
        return 'Git hooks stay on: no -c core.hooksPath override.'
    if i >= len(args):
        return None
    sub, rest = args[i], args[i + 1:]

    if sub == 'add' and any(a in ('-A', '--all', '.', ':/') for a in rest):
        return 'Stage by pathspec. Never git add -A or git add .: other sessions share this working tree.'
    if sub in ('commit', 'push', 'merge', 'rebase') and '--no-verify' in rest:
        return 'Never skip git hooks with --no-verify. Fix what the hook reports.'
    if sub == 'commit':
        flags = [a for a in rest if a.startswith('-') and not a.startswith('--')]
        if '-n' in flags:
            return 'Never skip git hooks with --no-verify. Fix what the hook reports.'
        if '--all' in rest or any('a' in f[1:] for f in flags if f[1:].isalpha()):
            return 'Commit by pathspec: git commit -- <paths>. Never commit -a: other sessions share this working tree.'
        if '--signoff' in rest or '--trailer' in rest or any('s' in f[1:] for f in flags if f[1:].isalpha()):
            return 'Commit messages carry no Co-Authored-By or other trailer.'
    if sub == 'tag' and rest and rest[0] not in TAG_READ_FLAGS:
        return 'Never create, move or delete git tags unless Mischa asks.'
    return None


def main():
    command = json.load(sys.stdin).get('tool_input', {}).get('command', '')
    reason = None

    if re.search(r'\bgit\b[^|;&]*\bcommit\b', command) and TRAILER.search(command):
        reason = 'Commit messages carry no Co-Authored-By or other trailer.'

    if not reason:
        try:
            for seg in segments(command):
                if 'git' in seg:
                    reason = git_violation(seg[seg.index('git') + 1:])
                elif any(t.endswith('pint') for t in seg) and '--dirty' in seg:
                    reason = 'Never pint --dirty: it formats files other sessions changed. The Stop hook formats the files you touched.'
                elif any(t.endswith('pint') for t in seg) and '--blade' in seg:
                    reason = "Never pint --blade: the Blade formatter moves whitespace around {{ }} and directives and changes the rendered text."
                if reason:
                    break
        except ValueError:
            pass

    if reason:
        print(json.dumps({'hookSpecificOutput': {
            'hookEventName': 'PreToolUse',
            'permissionDecision': 'deny',
            'permissionDecisionReason': reason,
        }}))


try:
    main()
except Exception:
    sys.exit(0)
