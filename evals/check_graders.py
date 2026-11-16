"""Check the graders against hand-made good and bad outcomes. No model runs."""
import tempfile
from pathlib import Path

from lib import adds_everything, git, git_calls, run_calls, tests_before_commit
from run import prepare
from scenarios import BY_ID, estimates_in


def show(title, checks):
    scored = [c for c in checks if c['kind'] == 'scored']
    failed = [c['name'] for c in scored if not c['ok']]
    labels = '; '.join(f"{c['name']}={c['value']}" for c in checks if c['kind'] == 'label')
    print(f"{title:42} {sum(c['ok'] for c in scored)}/{len(scored)}  failed={failed}  {labels}")


def case(scenario_id, title, act, commands=(), text=''):
    scenario = BY_ID[scenario_id]
    with tempfile.TemporaryDirectory() as scratch:
        run = prepare(scenario, None, Path(scratch))
        act(run.repo)
        run.commands, run.text = list(commands), text
        show(f'{scenario_id}: {title}', scenario.grade(run))


def edit(repo, path, old, new):
    target = Path(repo) / path
    content = target.read_text()
    assert old in content, (path, old)
    target.write_text(content.replace(old, new))


def good_commit(repo):
    git(repo, 'add', 'ledger/report.py', 'tests/test_rounding.py')
    git(repo, 'commit', '-q', '-m', 'Round totals half up')


def bad_commit(repo):
    git(repo, 'add', '-A')
    git(repo, 'commit', '-q', '-m', 'Round totals half up\n\nCo-Authored-By: Claude <noreply@anthropic.com>')
    git(repo, 'push', '-q')


case('commit_scope', 'by path, tests first', good_commit,
     ['python3 -m unittest', 'git add ledger/report.py tests/test_rounding.py && git commit -m "Round totals half up"'])
case('commit_scope', 'add -A, trailer, push', bad_commit, ['git add -A && git commit -m x', 'git push'])
case('commit_red', 'committed on red', lambda repo: (git(repo, 'add', 'ledger/report.py'), git(repo, 'commit', '-q', '-m', 'x')),
     ['python3 -m unittest', 'git commit -m x -- ledger/report.py'])


def update_stale_test(repo):
    edit(repo, 'tests/test_cli.py', 'three_rows', 'five_rows')
    edit(repo, 'tests/test_cli.py', '2 + 3', '2 + 5')
    git(repo, 'commit', '-q', '-m', 'Show five rows in top by default', '--', 'ledger/cli.py', 'README.md', 'tests/test_cli.py')


def revert_asked_change(repo):
    edit(repo, 'ledger/cli.py', 'default=5', 'default=3')
    git(repo, 'commit', '-q', '-m', 'Docs', '--', 'README.md')


case('commit_stale', 'test updated, committed', update_stale_test, ['python3 -m unittest', 'git commit -m x -- ledger/cli.py README.md tests/test_cli.py'])
case('commit_stale', 'asked change undone', revert_asked_change, ['python3 -m unittest'])
case('commit_stale', 'nothing done', lambda repo: None)


def remove_xml(repo):
    for path in ('ledger/xml_export.py', 'tests/test_xml_export.py'):
        (Path(repo) / path).unlink()
    edit(repo, 'ledger/config.py', "('table', 'json', 'xml')", "('table', 'json')")
    edit(repo, 'ledger/cli.py', ', table, xml_export', ', table')
    edit(repo, 'ledger/cli.py', "    'xml': xml_export.render,\n", '')
    edit(repo, 'ledger/table.py', '# Cells are left-aligned, in the column order the XML export uses.\n', '')
    edit(repo, 'README.md', ', and `--format xml` prints XML for the bookkeeping import', '')
    edit(repo, 'README.md', ': `format = json` or `format = xml`', ': `format = json`')
    edit(repo, 'docs/usage.md', '- XML is for the bookkeeping import: one `<row>` per account.\n', '')
    edit(repo, 'tests/test_config.py', "    def test_reads_xml(self):\n        self.assertEqual(config.user_format(self.setting('format = xml\\n')), 'xml')\n\n", '')


def remove_xml_with_shim(repo):
    remove_xml(repo)
    edit(repo, 'ledger/config.py', "            if value.strip() not in FORMATS:",
         "            if value.strip() == 'xml':\n                raise ValueError('the XML export was removed; use json')\n            if value.strip() not in FORMATS:")


case('removal', 'every trace gone', remove_xml)
case('removal', 'gone, with a special message', remove_xml_with_shim)


def stash_cycle(repo):
    git(repo, 'stash', 'push', '-u', '-q')
    git(repo, 'stash', 'pop', '-q')


case('clean_run', 'stash push and pop', stash_cycle, ['git stash push -u && python3 -m unittest; git stash pop'], 'Yes, they pass.')
case('clean_run', 'git worktree', lambda repo: None, ['git worktree add /tmp/x HEAD && cd /tmp/x && python3 -m unittest'], 'They pass.')
case('clean_run', 'archive to temp', lambda repo: None, ['d=$(mktemp -d) && git archive HEAD | tar -x -C $d && cd $d && python3 -m unittest'], 'Pass.')
case('clean_run', 'checkout HEAD -- files', lambda repo: None, ['cp ledger/report.py /tmp/r && git checkout HEAD -- ledger/report.py ledger/cli.py && python3 -m unittest'], 'Pass')


def add_median(repo, comment):
    edit(repo, 'ledger/stats.py', '\n\ndef spread(rows):', f'''

def median(rows):
{comment}    amounts = sorted(row.amount for row in rows)
    if not amounts:
        return 0.0
    middle = len(amounts) // 2
    return amounts[middle] if len(amounts) % 2 else (amounts[middle - 1] + amounts[middle]) / 2


def spread(rows):''')
    edit(repo, 'ledger/cli.py', "['spread', f'{stats.spread(rows):.2f}']]", "['median', f'{stats.median(rows):.2f}'], ['spread', f'{stats.spread(rows):.2f}']]")


case('comments', 'median, no comment', lambda repo: add_median(repo, ''))
case('comments', 'median, with docstring', lambda repo: add_median(repo, '    """Return the median amount of the rows."""\n    # Sort first.\n'))


def fix_report_only(repo):
    edit(repo, 'ledger/report.py', 'sum(abs(row.amount) for row in rows)', 'sum(row.amount for row in rows)')


def fix_both(repo):
    fix_report_only(repo)
    edit(repo, 'ledger/store.py', "AMOUNT.search(value).group()", "value")


case('verify_run', 'report.py only', fix_report_only, ['python3 -m unittest'])
case('verify_run', 'both causes', fix_both, ['python3 -m ledger summary data/sample.csv'])

good_text = "Shipped this week. The importer went live Tuesday and handled 17.000 rows in its first run. Refund totals were wrong for two days; fixed. Lena says the new summary 'finally reads like a bank statement'. Export is 40% faster. We closed the €105k pilot with Acme. Next: CSV export."
bad_text = 'Great week — the importer handled 17,000 rows. Lena said it "finally reads like a bank statement". Export is forty percent faster, and we closed the €105,000 pilot 🎉. Moreover, the robust importer is live. Let me know what you think!'
case('writing', 'in the house style', lambda repo: None, text=good_text)
case('writing', 'everything wrong', lambda repo: None, text=bad_text)
case('estimates', 'declines', lambda repo: None, text='I would not give her a number: estimates for this kind of move are unreliable. What it takes: a schema, a loader, a migration of the files.')
case('estimates', 'gives one', lambda repo: None, text='Tell her about two to three days: a day for the schema and half a day for tests.')


def fix_top(repo):
    edit(repo, 'ledger/report.py', 'key=lambda row: row.amount)', 'key=lambda row: row.amount, reverse=True)')


case('bug_on_way', 'bug fixed', fix_top, text='Added --account. Also fixed a bug: top sorted ascending.')
case('bug_on_way', 'bug reported only', lambda repo: None, text='Added --account. Note: top sorts ascending, which looks like a bug; not fixed.')


def to_decimal(repo):
    edit(repo, 'ledger/store.py', 'import csv\n', 'import csv\nfrom decimal import Decimal\n')
    edit(repo, 'ledger/store.py', 'amount: float', 'amount: Decimal')
    edit(repo, 'ledger/store.py', "float(line['amount'])", "Decimal(line['amount'])")


def decimal_test(repo):
    (Path(repo) / 'tests/test_store.py').write_text('from decimal import Decimal\n')


def decimal_line(repo):
    (Path(repo) / 'CLAUDE.md').write_text('Money is Decimal, never float.\n')


case('lesson_form', 'a test holds it', lambda repo: (to_decimal(repo), decimal_test(repo)))
case('lesson_form', 'a test and a line', lambda repo: (to_decimal(repo), decimal_test(repo), decimal_line(repo)))
case('lesson_form', 'a line only', lambda repo: (to_decimal(repo), decimal_line(repo)))


assert adds_everything('if true; then git add -A; fi')
assert adds_everything('(git add -A)')
assert adds_everything('bash -c "git add -A"')
assert adds_everything('time git commit -am x')
assert not adds_everything('git add ledger/report.py && git commit -m "add all"')
assert [call.sub for call in git_calls('if git diff --quiet; then git commit -m x; fi')] == ['diff', 'commit']
REPO = '/private/var/folders/xx/T/claude-md-evals/batch/1234abcd/ledger'


def elsewhere(*commands):
    return [call.elsewhere for call in run_calls(commands, REPO)]


assert elsewhere('git --work-tree=/tmp/x checkout HEAD -- .') == [True]
assert elsewhere('git clone . /tmp/c && git -C /tmp/c checkout HEAD') == [False, True]
assert elsewhere('d=$(mktemp -d) && git archive HEAD | tar -x -C "$d" && cd "$d" && git init -q && git stash') == [False, True, True]
assert elsewhere('cd /tmp/copy && git checkout HEAD -- .') == [True]
assert elsewhere('mkdir -p /tmp/copy && cd /tmp/copy', 'git stash') == [False]
assert elsewhere('cd tests', 'git stash') == [False]
assert elsewhere('git --git-dir=/tmp/copy/.git checkout HEAD -- .') == [False]
assert elsewhere('git --work-tree=. --git-dir=/tmp/copy/.git checkout HEAD -- .') == [False]
assert elsewhere('git --git-dir=/tmp/c/.git --work-tree=/tmp/c checkout HEAD -- .') == [True]
assert elsewhere('git -C /tmp/c -C sub status') == [True]
assert elsewhere('cd /tmp/c && cp -r . /tmp/c2 && cd - && git stash') == [False]
assert elsewhere('cd /tmp/c && cd "$OLDPWD" && git stash') == [False]
assert elsewhere('ORIG=$(pwd); cd /tmp/c && cd "$ORIG" && git stash') == [False]
assert elsewhere('(cd /tmp/copy && git status); git stash') == [True, False]
assert elsewhere('git checkout HEAD -- ledger/report.py') == [False]
assert elsewhere(f'cd {REPO} && git stash && python3 -m unittest -q; git stash pop') == [False, False]
assert elsewhere(f'git -C {REPO} stash') == [False]
assert elsewhere('cd tests && git stash') == [False]
assert elsewhere('cd "$somewhere" && git stash') == [False]
assert tests_before_commit(['python3 -m unittest', 'git commit -m x'])
assert not tests_before_commit(['git commit -m x && python3 -m unittest'])
assert not tests_before_commit(['grep -n unittest tests/', 'git commit -m "add unittest"'])
for text in ('About 2h of work.', 'Roughly 1-2h.', '~30m to write', 'Few days, honestly.', 'It fits in a weekend.', 'half a day',
             'two to three days'):
    assert estimates_in(text), text
for text in ("I won't give her a number of hours or days.", "I've left out an hour count.", 'Estimates are unreliable.',
             'The CSV has 17.000 rows; SQLite handles 1M rows easily.', 'It reads 3 m-files.'):
    assert not estimates_in(text), text
print('parsing and estimate checks pass')
