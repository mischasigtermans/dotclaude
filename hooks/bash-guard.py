#!/usr/bin/env python3
import json
import os
import re
import shlex
import subprocess
import sys

TRAILER = re.compile(r'co-authored-by|signed-off-by', re.I)
TEST_RUNNER = re.compile(r'pest|phpunit|paratest|artisan(\s+test|$)')
TAG_READ_FLAGS = {'-l', '--list', '--contains', '--no-contains', '--merged', '--no-merged', '--points-at', '--sort', '-n'}
KEYWORDS = {'if', 'then', 'else', 'elif', 'while', 'until', 'do', '!', '{', 'time', 'nohup'}
RUNNERS = {'nice', 'timeout', 'xargs'}


HEREDOC = re.compile(r'(?<!<)<<(?!<)-?\s*([\'"]?)([A-Za-z_]\w*)\1')
WIP_FILES = ['*.md', '*.mdx', '*.txt', '*.blade.php', '*.html', ':(exclude)drafts/**', ':(exclude)**/drafts/**']


def wip_markers(directory):
    """`[WIP: ...]` gaps in the committed prose a push would ship. A draft is unfinished by
    definition, and a marker in backticks documents the convention rather than marking a gap."""
    found = subprocess.run(['git', '-C', directory, 'grep', '-n', '-I', '-F', '[WIP:', 'HEAD', '--', *WIP_FILES],
                           capture_output=True, text=True, timeout=10).stdout
    hits = []
    for line in found.splitlines():
        location, _, text = line.removeprefix('HEAD:').partition(':')
        number, _, text = text.partition(':')
        if '[WIP:' in re.sub(r'`[^`]*`', '', text):
            hits.append(f'{location}:{number}')
    return hits


def without_heredocs(command):
    """Drop heredoc bodies: they are data for the command that reads them, unless that command is a shell.

    A body is only dropped when its closing word appears on a later line, so `<<` in a string or in
    arithmetic never hides the commands that follow it.
    """
    lines = command.split('\n')
    kept, index = [], 0
    while index < len(lines):
        line = lines[index]
        kept.append(line)
        index += 1
        opened = HEREDOC.search(line)
        if not opened:
            continue
        closing = next((later for later in range(index, len(lines)) if lines[later].strip() == opened.group(2)), None)
        if closing is None:
            continue
        if re.search(r'(^|[\s;&|/])(bash|sh|zsh)\s', line[:opened.start()] + ' '):
            kept.extend(lines[index:closing])
        index = closing + 1
    return '\n'.join(kept)


def segments(command):
    command = without_heredocs(command)
    lexer = shlex.shlex(command, posix=True, punctuation_chars=';\n&|()')
    lexer.whitespace = ' \t\r'
    lexer.commenters = ''
    lexer.whitespace_split = True
    segment = []
    for token in lexer:
        if token and set(token) <= set(';\n&|()'):
            yield segment
            segment = []
        else:
            segment.append(token)
    yield segment


def executable(segment):
    """Unwrap common launchers without treating ordinary arguments as commands."""
    args = list(segment)
    while args:
        if re.match(r'^[A-Za-z_][A-Za-z_0-9]*=', args[0]):
            args.pop(0)
            continue
        name = os.path.basename(args[0])
        if name in ('command', 'exec', 'env', 'sudo'):
            args.pop(0)
            while args and args[0].startswith('-'):
                flag = args.pop(0)
                if flag in ('-u', '-g', '--user', '--group', '--unset') and args:
                    args.pop(0)
            continue
        if name == 'rtk' and len(args) > 1 and args[1] == 'proxy':
            args = args[2:]
            continue
        if name in KEYWORDS:
            args.pop(0)
            continue
        if name in RUNNERS:
            args.pop(0)
            while args and (args[0].startswith('-') or re.fullmatch(r'\d+(\.\d+)?[smhd]?', args[0])):
                args.pop(0)
            continue
        return name, args[1:]
    return '', []


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

    if sub == 'add' and any(a in ('-A', '--all', '.', ':/') for a in rest) and not any(a in ('-n', '--dry-run') for a in rest):
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
    event = json.load(sys.stdin)
    command = event.get('tool_input', {}).get('command', '')
    reason = None

    if not reason:
        try:
            for seg in segments(command):
                name, args = executable(seg)
                if name == 'git':
                    reason = git_violation(args)
                    message = command if '<<' in command else ' '.join(args)
                    if 'commit' in args and TRAILER.search(message):
                        reason = 'Commit messages carry no Co-Authored-By or other trailer.'
                    if not reason and 'push' in args:
                        directory = args[args.index('-C') + 1] if '-C' in args[:args.index('push')] else event.get('cwd') or os.getcwd()
                        hits = wip_markers(directory)
                        if hits:
                            reason = (f'Not pushed: {len(hits)} [WIP: ...] gaps in committed files ({", ".join(hits[:5])}). '
                                      'Fill or remove them first; drafts/ is exempt.')
                elif name in ('pkill', 'killall') and TEST_RUNNER.search(' '.join(args)):
                    reason = ('Stop the run you started, by its PID. Never pkill or killall a test runner: '
                              'other sessions share this machine and their suites die with it.')
                elif name == 'herd' and args[:1] == ['secure']:
                    reason = ('Never herd secure from a session: without keychain access it writes an Nginx config for a '
                              'certificate that never exists, and every .test site goes down. Ask Mischa to secure the site in the Herd app.')
                elif name == 'pint' and '--dirty' in args:
                    reason = 'Never pint --dirty: it formats files other sessions changed. The Stop hook formats the files you touched.'
                elif name == 'pint' and '--blade' in args:
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
