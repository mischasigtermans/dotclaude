#!/usr/bin/env python3
import json
from difflib import SequenceMatcher
import os
import re
import sys

MIN_WORDS = 150
MIN_TEMPLATE_WORDS = 50
MIN_RUN_WORDS = 5
PROSE_EXT = ('.md', '.mdx', '.txt')
TEMPLATE_EXT = ('.blade.php', '.html', '.htm', '.vue', '.svelte', '.astro', '.twig')
LANG_PATH = re.compile(r'/(lang|content)/.+\.(php|json)$')
SKIP_PATH = re.compile(r'/\.claude/|/\.ai/|/node_modules/|/vendor/|/SKILL\.md$|/CLAUDE\.md$|/AGENTS\.md$'
                       r'|^/(private/)?tmp/|/scratchpad/|/\.panels/|/projects/[^/]+/memory/')
CONFIG_DIR = os.environ.get('CLAUDE_CONFIG_DIR', '').rstrip('/')

INLINE = r'a|abbr|b|br|cite|code|em|i|kbd|mark|q|s|small|span|strong|sub|sup|u|wbr'
TAG = r'''(?:"[^"]*"|'[^']*'|[^>"'])*>'''
BREAK = '\x00'
ATTR = re.compile(r'''(?<![\w:@.-])([a-zA-Z][\w-]*)=(?:"([^"]*)"|'([^']*)')''')
CODE_ATTR = re.compile(r'^(class|style|href|src|srcset|sizes|id|name|type|value|for|action|method|rel|target|d|points|viewbox|'
                       r'x-.*|data-.*|on[a-z]+)$', re.I)


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
    return call.get('name') == 'Skill' and call.get('input', {}).get('skill', '').split(':')[-1] in ('copywriter', 'sharpen')


def props(tag):
    """A tag's copy: the static attribute values that hold words for the visitor, such as title, lead and alt."""
    values = (double or single for name, double, single in ATTR.findall(tag.group()) if not CODE_ATTR.match(name))
    return BREAK + BREAK.join(values) + BREAK


def visible(text):
    """The sentences a visitor reads in a template. Markup, directives, code and echoes go,
    and so does any run of text under MIN_RUN_WORDS: labels, buttons, nav items, table headers."""
    text = re.sub(r'\{\{--.*?--\}\}|<!--.*?-->|\{#.*?#\}', BREAK, text, flags=re.S)
    text = re.sub(r'@php\b.*?@endphp|<\?php.*?\?>|<(script|style|svg|pre|code)\b.*?</\1>|^---\n.*?\n---\n',
                  BREAK, text, flags=re.S)
    text = re.sub(r'\{\{.*?\}\}|\{!!.*?!!\}|\{%.*?%\}', ' ', text, flags=re.S)
    text = re.sub(r'@\w+(\s*\((?:[^()]|\((?:[^()]|\([^()]*\))*\))*\))?', BREAK, text)
    text = re.sub(rf'</?(?:{INLINE})\b{TAG}', ' ', text, flags=re.I)
    text = re.sub(rf'</?[a-zA-Z]{TAG}', props, text)
    runs = (' '.join(run.split()) for run in text.split(BREAK))
    return '\n'.join(run for run in runs if len(words(run)) >= MIN_RUN_WORDS)


def strings(text):
    """The sentences in a lang or content file: every string literal, under the same run rule."""
    values = re.findall(r'''"((?:[^"\\]|\\.)*)"|'((?:[^'\\]|\\.)*)\'''', text)
    runs = (re.sub(r'<[^>]*>|:\w+|\{\w+\}', ' ', double or single) for double, single in values)
    return '\n'.join(run for run in runs if len(words(run)) >= MIN_RUN_WORDS)


def prose(call, originals):
    """The file a call wrote, its new and old text, and whether it is a template or lang file."""
    name, args = call.get('name', ''), call.get('input', {})
    path = args.get('file_path', '')
    extract = strings if LANG_PATH.search(path) else visible if path.endswith(TEMPLATE_EXT) else None
    if name not in ('Write', 'Edit') or not (extract or path.endswith(PROSE_EXT)) or skipped(path):
        return None, '', '', False
    if name == 'Write':
        new, old = args.get('content') or '', originals.get(call.get('id'), '')
    else:
        new, old = args.get('new_string') or '', args.get('old_string') or ''
    return (path, extract(new), extract(old), True) if extract else (path, new, old, False)


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

    written, in_templates, targets = 0, 0, []
    for call in current:
        if is_sharpen(call):
            written, in_templates, targets = 0, 0, []
            continue
        target, new, old, template = prose(call, originals)
        if not target:
            continue
        count = changed_words(old, new)
        if not count:
            continue
        if template:
            in_templates += count
        else:
            written += count
        if target not in targets:
            targets.append(target)

    if written >= MIN_WORDS or in_templates >= MIN_TEMPLATE_WORDS:
        print(json.dumps({
            'decision': 'block',
            'reason': f'{written + in_templates} words of new copy in '
                      f'{", ".join(os.path.basename(target) for target in targets)}. '
                      'Run the copywriter skill on it before you finish.',
        }))


try:
    main()
except Exception:
    sys.exit(0)
