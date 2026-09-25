#!/usr/bin/env python3
import json
import re
import sys

MIN_WORDS = 150
PROSE_EXT = ('.md', '.mdx', '.txt')
SKIP_PATH = re.compile(r'/\.claude/|/\.ai/|/node_modules/|/vendor/|/SKILL\.md$|/CLAUDE\.md$|/AGENTS\.md$')
DRAFT_TOOL = re.compile(r'mail_compose|mail_reply|mail_forward|create_email_draft|create_reply_draft|create_forward_draft|bear__create_note|bear__overwrite_note')


def current_turn(transcript_path):
    turn = []
    with open(transcript_path) as f:
        for line in f:
            entry = json.loads(line)
            content = entry.get('message', {}).get('content')
            if entry.get('type') == 'user' and isinstance(content, str):
                turn = []
            elif entry.get('type') == 'assistant' and isinstance(content, list):
                turn += [c for c in content if c.get('type') == 'tool_use']
    return turn


def prose(call):
    name, args = call.get('name', ''), call.get('input', {})
    if name in ('Write', 'Edit'):
        path = args.get('file_path', '')
        if not path.endswith(PROSE_EXT) or SKIP_PATH.search(path):
            return None, ''
        return path, args.get('content') or args.get('new_string') or ''
    if DRAFT_TOOL.search(name):
        return name.split('__')[-1], ' '.join(str(v) for k, v in args.items() if k in ('body', 'content', 'text', 'message'))
    return None, ''


def main():
    event = json.load(sys.stdin)
    if event.get('stop_hook_active'):
        return

    words, targets = 0, []
    for call in current_turn(event['transcript_path']):
        if call.get('name') == 'Skill' and call.get('input', {}).get('skill') == 'sharpen':
            return
        target, text = prose(call)
        if not target:
            continue
        text = re.sub(r'```.*?```', '', text, flags=re.S)
        text = re.sub(r'^---\n.*?\n---\n', '', text, flags=re.S)
        words += len(re.findall(r'[^\W\d_]{2,}', text))
        if target not in targets:
            targets.append(target)

    if words >= MIN_WORDS:
        print(json.dumps({
            'decision': 'block',
            'reason': f'You wrote {words} words of prose this turn ({", ".join(targets)}). '
                      'Run the sharpen skill on it in self-check mode before you finish.',
        }))


try:
    main()
except Exception:
    sys.exit(0)
