#!/usr/bin/env python3
import argparse
import json
import os
import re
import sys
import time
from collections import Counter
from datetime import date, datetime
from pathlib import Path

STATES = ('accepted', 'rejected', 'not-applied', 'run')
FIELDS = {'target', 'kind', 'state', 'sessions', 'note', 'folders'}
KINDS = ('prompt', 'interrupt', 'denial', 'block', 'broken', 'error', 'calls')
DENIAL = re.compile(r'PreToolUse:(\w+) hook error: ')
NOISE = re.compile(r'<(system-reminder|local-command-\w+|task-notification)\b.*?</\1>', re.S)
INTERRUPT = '[Request interrupted by user'


def slug(path):
    return re.sub(r'[^A-Za-z0-9-]', '-', str(path))


def name(repo):
    return 'home' if repo == Path.home() else repo.name.lstrip('.')


def text_of(content):
    if isinstance(content, str):
        return content
    return ' '.join(part.get('text', '') for part in content or [] if isinstance(part, dict) and part.get('type') == 'text')


def events(path, calls=None):
    """Yields (timestamp, kind, detail) for what a person typed and what went wrong in one session file.
    Lines are filtered as text before they are parsed: a session runs to megabytes of tool output.
    With calls, each tool call is kept there by id, so an error can name the command behind it.
    Without, tool calls are only counted, unparsed."""
    with open(path, errors='replace') as lines:
        for line in lines:
            if '"type":"assistant"' in line:
                if calls is None:
                    if '"tool_use"' in line:
                        yield '', 'calls', line.count('"type":"tool_use"')
                    continue
                if '"tool_use"' not in line:
                    continue
            elif '"type":"user"' in line:
                if '"tool_result"' in line and '"is_error":true' not in line:
                    continue
            elif '"hook_' not in line:
                continue
            try:
                entry = json.loads(line)
            except ValueError:
                continue
            kind, when = entry.get('type'), entry.get('timestamp', '')
            content = (entry.get('message') or {}).get('content')
            if kind == 'attachment':
                hook = entry.get('attachment') or {}
                if hook.get('type') == 'hook_blocking_error':
                    reason = hook.get('blockingError')
                    reason = reason.get('blockingError') if isinstance(reason, dict) else reason
                    yield when, 'block', (hook.get('hookName'), reason)
                elif hook.get('type') == 'hook_non_blocking_error':
                    yield when, 'broken', (hook.get('hookName'), hook.get('stderr'))
            elif kind == 'assistant':
                for part in content or []:
                    if isinstance(part, dict) and part.get('type') == 'tool_use':
                        args = part.get('input') or {}
                        calls[part.get('id')] = (part.get('name', ''), args.get('command') or args.get('file_path') or '')
                        yield when, 'call', (part.get('name', ''), args.get('pattern') or '')
            elif kind == 'user' and not entry.get('isMeta'):
                for part in content if isinstance(content, list) else []:
                    if isinstance(part, dict) and part.get('type') == 'tool_result' and part.get('is_error'):
                        tool, command = (calls or {}).get(part.get('tool_use_id'), ('', ''))
                        text = text_of(part.get('content'))
                        denied = DENIAL.match(text)
                        if denied:
                            yield when, 'denial', (denied.group(1), command, text[denied.end():])
                        else:
                            yield when, 'error', (tool, command, text)
                text = text_of(content)
                origin = entry.get('origin')
                if text.startswith(INTERRUPT):
                    yield when, 'interrupt', ()
                elif isinstance(origin, dict) and origin.get('kind') == 'human' and NOISE.sub('', text).strip():
                    yield when, 'prompt', (NOISE.sub('', text).strip(),)


def subagents(path):
    return sorted((path.parent / path.stem / 'subagents').glob('agent-*.jsonl'))


def tally(path):
    counts = dict.fromkeys(KINDS, 0)
    for file in [path, *subagents(path)]:
        for _, kind, detail in events(file):
            counts[kind] += detail if kind == 'calls' else 1
    return counts


def recent(folder, since):
    return [path for path in folder.glob('*.jsonl') if path.stat().st_mtime >= since]


def records(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()] if path.exists() else []


def last(entries, key):
    return next((entry[key] for entry in reversed(entries) if entry.get(key)), None)


def scope(args):
    """The folders to read and the moment to read from. Folders named with --also and the date of
    the last run come from the ledger when the call leaves them out."""
    repo = Path(args.repo).expanduser().resolve()
    entries = records(Path(args.store).expanduser() / name(repo) / 'ledger.jsonl')
    also = args.also or last(entries, 'folders') or []
    paths = [repo, *(Path(path).expanduser().resolve() for path in also)]
    if args.since:
        since = datetime.fromisoformat(args.since).timestamp()
    elif args.days is None and entries:
        since = datetime.fromisoformat(entries[-1]['date']).timestamp()
    else:
        since = time.time() - (args.days or 14) * 86400
    return repo, paths, since


def related(folder, repo):
    """A session folder that may hold this repo's work too: one of the same name elsewhere, or one inside the repo."""
    if repo == Path.home():
        return False
    return folder.endswith('-' + name(repo).lower()) or folder.startswith(slug(repo).lower() + '-')


def cmd_sessions(args):
    repo, paths, since = scope(args)
    projects = Path(args.projects).expanduser()
    folders = {projects / slug(path): path for path in paths}
    current = os.environ.get('CLAUDE_CODE_SESSION_ID')
    found = [(path, origin) for folder, origin in folders.items() for path in recent(folder, since) if path.stem != current]
    for path, origin in sorted(found, key=lambda pair: pair[0].stat().st_mtime, reverse=True):
        stat = path.stat()
        print(json.dumps({'id': path.stem, 'folder': str(origin), 'date': date.fromtimestamp(stat.st_mtime).isoformat(),
                          'mb': round(stat.st_size / 1e6, 1), 'subagents': len(subagents(path)), **tally(path)}))
    others = {folder.name: len(recent(folder, since)) for folder in projects.iterdir()
              if folder.is_dir() and folder not in folders and related(folder.name.lower(), repo)}
    print(json.dumps({'read': [str(path) for path in paths], 'sessions': len(found),
                      'not_read': {folder: count for folder, count in others.items() if count}}))


def clip(text, limit):
    text = ' '.join(str(text).split())
    return text if len(text) <= limit else text[:limit] + ' ...'


def render(path):
    """One session as text. The calls between two events are one line: how many per tool, and what was searched for."""
    files = [path, *subagents(path)]
    lines = [f'session {path.stem} | {date.fromtimestamp(path.stat().st_mtime).isoformat()} | {len(files) - 1} subagents']
    for file in files:
        if file != path:
            lines.append(f'-- subagent {file.stem}')
        tools, searched = Counter(), []

        def flush():
            if tools:
                counts = ', '.join(f'{tool} {count}' for tool, count in tools.most_common())
                lines.append(f'  calls: {counts}' + (f' | searched: {clip("; ".join(searched), 300)}' if searched else ''))
                tools.clear()
                searched.clear()

        for when, kind, detail in events(file, {}):
            stamp = when[:16].replace('T', ' ')
            if kind == 'call':
                tools[detail[0]] += 1
                if detail[1]:
                    searched.append(detail[1])
                continue
            flush()
            if kind == 'prompt':
                lines.append(f'[{stamp}] prompt: {clip(detail[0], 600)}')
            elif kind == 'interrupt':
                lines.append(f'[{stamp}] interrupt')
            elif kind in ('denial', 'error'):
                tool, command, reason = detail
                lines.append(f'[{stamp}] {kind} {tool}: {clip(command, 200)} | {clip(reason, 300)}')
            else:
                lines.append(f'[{stamp}] {kind} {detail[0]}: {clip(detail[1], 300)}')
        flush()
    return '\n'.join(lines) + '\n'


def cmd_extract(args):
    _, paths, _ = scope(args)
    projects = Path(args.projects).expanduser()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    for prefix in args.ids:
        matches = [path for origin in paths for path in (projects / slug(origin)).glob(f'{prefix}*.jsonl')]
        if len(matches) != 1:
            sys.exit(f'{prefix}: {len(matches)} sessions match')
        (out / f'{matches[0].stem}.txt').write_text(render(matches[0]))
        print(out / f'{matches[0].stem}.txt')


def cmd_ledger(args):
    repo = Path(args.repo).expanduser().resolve()
    path = Path(args.store).expanduser() / name(repo) / 'ledger.jsonl'
    if args.action == 'add':
        record = json.load(sys.stdin)
        if record.get('state') not in STATES or set(record) - FIELDS:
            sys.exit(f'a record has a state of {", ".join(STATES)} and only the fields {", ".join(sorted(FIELDS))}')
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'a') as ledger:
            ledger.write(json.dumps({'date': date.today().isoformat(), **record}) + '\n')
        return
    entries = records(path)
    latest = {(entry.get('target'), entry.get('kind')): entry for entry in entries if entry['state'] != 'run'}
    for (target, kind), entry in latest.items():
        if args.target in (None, target) and args.kind in (None, kind):
            print(json.dumps(entry))
    print(json.dumps({'last_run': entries[-1]['date'] if entries else None, 'folders': last(entries, 'folders') or []}))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--projects', default='~/.claude/projects', help=argparse.SUPPRESS)
    parser.add_argument('--store', default='~/.claude/retros', help=argparse.SUPPRESS)
    commands = parser.add_subparsers(dest='command', required=True)

    def scoped(command, run, help):
        sub = commands.add_parser(command, help=help)
        sub.add_argument('--repo', required=True)
        sub.add_argument('--also', nargs='*', help='other folders whose sessions worked on this repo, such as a lead\'s')
        sub.add_argument('--days', type=int)
        sub.add_argument('--since', help='YYYY-MM-DD')
        sub.set_defaults(run=run)
        return sub

    scoped('sessions', cmd_sessions, 'the repo\'s sessions in the window, newest first, with what went wrong in each')
    extract = scoped('extract', cmd_extract, 'one text file per session: prompts, hook denials and blocks, tool errors')
    extract.add_argument('--out', required=True)
    extract.add_argument('ids', nargs='+', help='session ids or unique prefixes')
    ledger = commands.add_parser('ledger', help='the decisions of earlier retros')
    ledger.add_argument('action', choices=('add', 'read'))
    ledger.add_argument('--repo', required=True)
    ledger.add_argument('--target')
    ledger.add_argument('--kind')
    ledger.set_defaults(run=cmd_ledger)

    args = parser.parse_args()
    args.run(args)


if __name__ == '__main__':
    main()
