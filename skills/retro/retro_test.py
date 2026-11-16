#!/usr/bin/env python3
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).parent
REPO = '/p/site'
LEAD = '/p/lead'


class RetroTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        self.session('-p-site', 'aaaa1111')
        self.session('-p-lead', 'bbbb2222')
        self.session('-p-site-archive', 'cccc3333')
        self.session('-q-Site', 'dddd4444')
        self.session('-q-website-notes', 'eeee5555')
        subagent = self.tmp / 'projects/-p-site/aaaa1111/subagents/agent-x1.jsonl'
        subagent.parent.mkdir(parents=True)
        shutil.copy(HERE / 'fixture.jsonl', subagent)

    def session(self, folder, session_id):
        target = self.tmp / 'projects' / folder / f'{session_id}.jsonl'
        target.parent.mkdir(parents=True)
        shutil.copy(HERE / 'fixture.jsonl', target)

    def run_retro(self, *args, stdin=None, session=''):
        return subprocess.run(
            [sys.executable, '-B', str(HERE / 'retro.py'), '--projects', str(self.tmp / 'projects'),
             '--store', str(self.tmp / 'retros'), *args],
            input=stdin, capture_output=True, text=True, env={**os.environ, 'CLAUDE_CODE_SESSION_ID': session})

    def sessions(self, *args, **kwargs):
        lines = [json.loads(line) for line in self.run_retro('sessions', '--repo', REPO, *args, **kwargs).stdout.splitlines()]
        return lines[:-1], lines[-1]

    def test_counts_what_went_wrong_and_folds_in_the_subagent(self):
        rows, _ = self.sessions()
        self.assertEqual([row['id'] for row in rows], ['aaaa1111'])
        counts = {kind: rows[0][kind] for kind in ('prompt', 'interrupt', 'denial', 'block', 'broken', 'error')}
        self.assertEqual(counts, dict.fromkeys(counts, 2))
        self.assertEqual(rows[0]['calls'], 8)
        self.assertEqual(rows[0]['subagents'], 1)

    def test_names_the_folders_it_did_not_read(self):
        _, summary = self.sessions()
        self.assertEqual(summary['not_read'], {'-p-site-archive': 1, '-q-Site': 1})

    def test_reads_a_related_folder_and_skips_the_running_session(self):
        rows, summary = self.sessions('--also', LEAD, session='aaaa1111')
        self.assertEqual([row['id'] for row in rows], ['bbbb2222'])
        self.assertEqual(summary['read'], [REPO, LEAD])

    def test_remembers_related_folders_from_the_ledger(self):
        self.run_retro('ledger', 'add', '--repo', REPO, stdin=json.dumps({'state': 'run', 'folders': [LEAD]}))
        rows, _ = self.sessions('--days', '14')
        self.assertEqual({row['id'] for row in rows}, {'aaaa1111', 'bbbb2222'})

    def test_extract_names_the_command_behind_a_denial_and_drops_injected_text(self):
        out = self.tmp / 'out'
        self.run_retro('extract', '--repo', REPO, '--out', str(out), 'aaaa')
        text = (out / 'aaaa1111.txt').read_text()
        self.assertIn('denial Bash: git add -A | Stage by pathspec', text)
        self.assertIn('error Bash: vendor/bin/pest tests/ExportTest.php | Exit code 1 FAILED', text)
        self.assertIn('block Stop: You wrote 200 words', text)
        self.assertIn('broken Stop: Hook script appears to be missing', text)
        self.assertIn('prompt: Rename the export job', text)
        self.assertIn('calls: Read 1, Grep 1 | searched: ExportJob', text)
        self.assertIn('-- subagent agent-x1', text)
        self.assertNotIn('never shown', text)
        self.assertNotIn('Another Claude session', text)

    def test_ledger_keeps_the_latest_decision_per_target_and_kind(self):
        first = {'target': 'CLAUDE.md', 'kind': 'stale path', 'state': 'rejected', 'note': 'still needed'}
        self.run_retro('ledger', 'add', '--repo', REPO, stdin=json.dumps(first))
        self.run_retro('ledger', 'add', '--repo', REPO, stdin=json.dumps({**first, 'state': 'accepted', 'note': 'gone'}))
        lines = [json.loads(line) for line in self.run_retro('ledger', 'read', '--repo', REPO).stdout.splitlines()]
        self.assertEqual([(line['state'], line['note']) for line in lines[:-1]], [('accepted', 'gone')])
        self.assertTrue(lines[-1]['last_run'])

    def test_ledger_refuses_an_unknown_state_or_field(self):
        for record in ({'state': 'maybe'}, {'state': 'accepted', 'transcript': 'pasted text'}):
            self.assertNotEqual(self.run_retro('ledger', 'add', '--repo', REPO, stdin=json.dumps(record)).returncode, 0)
        self.assertFalse((self.tmp / 'retros').exists())


if __name__ == '__main__':
    unittest.main()
