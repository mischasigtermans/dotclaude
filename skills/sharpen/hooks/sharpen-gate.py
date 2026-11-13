#!/usr/bin/env python3
import json
from difflib import SequenceMatcher
import os
import re
import sys

MIN_WORDS = 150
PROSE_EXT = ('.md', '.mdx', '.txt')
SKIP_PATH = re.compile(r'/\.claude/|/\.ai/|/node_modules/|/vendor/|/SKILL\.md$|/CLAUDE\.md$|/AGENTS\.md$')
CONFIG_DIR = os.environ.get('CLAUDE_CONFIG_DIR', '').rstrip('/')


def skipped(path):
    return bool(SKIP_PATH.search(path)) or bool(CONFIG_DIR) and path.startswith(CONFIG_DIR + '/')


def is_prompt(content):
    """A user entry the user typed: a string, or parts (text, image) with no tool result among them."""
    if isinstance(content, str):
        return True
    return isinstance(content, list) and not any(part.get('type') == 'tool_result' for part in content)


def turns(transcript_path):
    """The tool calls of the previous and the current turn, and the old text of each file a call replaced."""
    previous, current, originals = [], [], {}
    with open(transcript_path) as f:
        for line in f:
            entry = json.loads(line)
            if entry.get('isMeta'):
                continue
            content = entry.get('message', {}).get('content')
            if entry.get('type') == 'user' and is_prompt(content):
                previous, current = current, []
            elif entry.get('type') == 'user':
                result = entry.get('toolUseResult')
                if isinstance(result, dict) and isinstance(result.get('originalFile'), str):
                    for part in content:
                        originals[part.get('tool_use_id')] = result['originalFile']
            elif entry.get('type') == 'assistant' and isinstance(content, list):
                current += [c for c in content if c.get('type') == 'tool_use']
    return previous, current, originals


def is_sharpen(call):
    return call.get('name') == 'Skill' and call.get('input', {}).get('skill', '').split(':')[-1] == 'sharpen'


def prose(call, originals):
    name, args = call.get('name', ''), call.get('input', {})
    path = args.get('file_path', '')
    if name not in ('Write', 'Edit') or not path.endswith(PROSE_EXT) or skipped(path):
        return None, '', ''
    if name == 'Write':
        return path, args.get('content') or '', originals.get(call.get('id'), '')
    return path, args.get('new_string') or '', args.get('old_string') or ''


def words(text):
    text = re.sub(r'```.*?```', '', text, flags=re.S)
    text = re.sub(r'^---\n.*?\n---\n', '', text, flags=re.S)
    return re.findall(r'[^\W\d_]{2,}', text)


def changed_words(old, new):
    before, after = words(old), words(new)
    return sum(j2 - j1 for tag, _, _, j1, j2 in
               SequenceMatcher(None, before, after, autojunk=False).get_opcodes()
               if tag in ('insert', 'replace'))


def main():
    event = json.load(sys.stdin)
    if event.get('stop_hook_active'):
        return

    _, current, originals = turns(event['transcript_path'])

    words, targets = 0, []
    for call in current:
        if is_sharpen(call):
            words, targets = 0, []
            continue
        target, new, old = prose(call, originals)
        if not target:
            continue
        words += changed_words(old, new)
        if target not in targets:
            targets.append(target)

    if words >= MIN_WORDS:
        print(json.dumps({
            'decision': 'block',
            'reason': f'You wrote {words} words of prose this turn ({", ".join(targets)}). '
                      'Call the Skill tool with "sharpen" to check that prose before you finish. '
                      'Use self-check mode for your own copy. For a user draft with an approved diagnosis, '
                      'verify that diagnosis and its eval without asking for approval again.',
        }))


try:
    main()
except Exception:
    sys.exit(0)
