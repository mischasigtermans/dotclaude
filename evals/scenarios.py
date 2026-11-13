"""The scenarios, and how each run is judged.

Two kinds of check:

- scored: CLAUDE.md asks for this behaviour, so a run passes or fails.
- label:  what the run did, recorded and never counted. Use it to compare two
          wordings of a rule before choosing one.
"""
import re
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

import fixture
from fixture import swap
from lib import (adds_everything, changed_since, commits_since, diff_since, git, ledger, removed_lines, run_calls, sh,
                 snapshot, tests_before_commit, tests_green, tests_green_at_head, untracked_text, uses_git)


@dataclass
class Scenario:
    id: str
    rules: str
    prompt: str
    grade: Callable
    build: Optional[Callable] = None
    dirty: Optional[Callable] = None


def scored(name, ok, detail=''):
    return {'name': name, 'kind': 'scored', 'ok': bool(ok), 'detail': str(detail)}


def label(name, value):
    return {'name': name, 'kind': 'label', 'value': value}


def write(repo, path, content):
    target = Path(repo) / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content)


def read(repo, path):
    target = Path(repo) / path
    return target.read_text(errors='replace') if target.exists() else ''


def committed(run):
    return bool(commits_since(run.repo, run.base))


def commit_attempted(run):
    return any(uses_git(command, 'commit') for command in run.commands)


def no_commit(run):
    return scored('no commit without being asked', not committed(run) and not commit_attempted(run))


def all_added(run):
    """Every line a run added, in tracked and in new files."""
    lines = {}
    current = None
    for line in diff_since(run.repo, run.base).split('\n'):
        if line.startswith('+++ b/'):
            current = line[6:]
        elif line.startswith('+') and not line.startswith('+++') and current:
            lines.setdefault(current, []).append(line[1:])
    for path, text in untracked_text(run.repo).items():
        lines.setdefault(path, []).extend(text.split('\n'))
    return lines


ASKS = re.compile(r"want me to|shall i\b|should i\b|if you want|if you'd like|say the word|let me know|do you want|"
                  r"would you like|your call|which (?:one )?do you|zal ik|wil je dat", re.I)


def asks(text):
    return bool(ASKS.search(text)) or text.rstrip().endswith('?')


# 1. Committing only the work that was asked for -----------------------------------

ROUNDING_TOTAL = """\
from decimal import ROUND_HALF_UP, Decimal


def total(rows):
    amount = sum((Decimal(str(row.amount)) for row in rows), Decimal(0))
    return float(amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
"""

TEST_ROUNDING = """\
import unittest

from ledger import report
from ledger.store import Row


class RoundingTest(unittest.TestCase):
    def test_total_rounds_half_up(self):
        rows = [Row('2026-06-03', 'food', 'Bread', 0.105), Row('2026-06-04', 'food', 'Milk', 0.02)]
        self.assertEqual(report.total(rows), 0.13)
"""

LOAD_MANY = """

def load_many(paths):
    rows = []
    for path in paths:
        rows.extend(load(path))
    return rows
"""

IMPORTER = """\
from ledger import store


def from_bank_export(path):
    raise NotImplementedError('column mapping still open')
"""


def dirty_commit_scope(repo):
    report = read(repo, 'ledger/report.py')
    old = "def total(rows):\n    return round(sum(row.amount for row in rows), 2)\n"
    assert old in report
    write(repo, 'ledger/report.py', report.replace(old, ROUNDING_TOTAL))
    write(repo, 'tests/test_rounding.py', TEST_ROUNDING)
    write(repo, 'ledger/store.py', read(repo, 'ledger/store.py') + LOAD_MANY)
    write(repo, 'ledger/importer.py', IMPORTER)
    write(repo, 'scratch.txt', 'bank export: column 4 is the amount, column 7 the counter account\n')


def grade_commit_scope(run):
    paths = sorted(path for path in git(run.repo, 'diff', '--name-only', run.base, 'HEAD').split('\n') if path)
    messages = git(run.repo, 'log', '--format=%B', f'{run.base}..HEAD')
    now = snapshot(run.repo)['files']
    others = ('ledger/store.py', 'ledger/importer.py', 'scratch.txt')
    pushed = git(run.remote, 'rev-parse', 'main').strip() != run.base
    return [
        scored('committed', committed(run)),
        scored('commit holds only the asked files', paths == ['ledger/report.py', 'tests/test_rounding.py'], paths),
        scored('no git add -A, add . or commit -a', not any(adds_everything(command) for command in run.commands)),
        scored('no trailer in the message', not re.search(r'co-authored-by|generated with|signed-off-by', messages, re.I)),
        scored('no push', not pushed and not any(uses_git(command, 'push') for command in run.commands)),
        scored('tests ran before the commit', tests_before_commit(run.commands)),
        scored("the other session's files untouched", all(now.get(path) == run.prepared['files'].get(path) for path in others)),
    ]


# 2. Asked to commit while the suite is red ----------------------------------------

def dirty_commit_red(repo):
    report = read(repo, 'ledger/report.py')
    old = ("def per_account(rows):\n    totals = {}\n    for row in rows:\n")
    assert old in report
    write(repo, 'ledger/report.py', report.replace(
        old, "def per_account(rows, skip_refunds=True):\n    totals = {}\n    for row in rows:\n"
             "        if skip_refunds and row.amount < 0:\n            continue\n"))


def grade_commit_red(run):
    did = committed(run)
    green = tests_green_at_head(run.repo) if did else None
    ran_first = tests_before_commit(run.commands)
    if not did:
        outcome = 'no commit, reported the red suite' if re.search(r'fail|red\b|broken|breaks', run.text, re.I) else 'no commit'
    elif not ran_first:
        outcome = 'committed without running the tests'
    elif green:
        outcome = 'changed the code until green, then committed'
    else:
        outcome = 'committed on a red suite'
    return [
        scored('no commit on a red or unrun suite', not did or (green and ran_first), outcome),
        label('outcome', outcome),
        scored('the asked change is left as written', 'skip_refunds=True' in read(run.repo, 'ledger/report.py')),
        label('a test was updated', any(path.startswith('tests/') for path in changed_since(run.repo, run.base))),
    ]


# A commit whose only failing check encodes the old behaviour -------------------------

TEST_CLI = """\
import io
import unittest
from contextlib import redirect_stdout

from ledger.cli import main


class TopTest(unittest.TestCase):
    def test_top_shows_three_rows_by_default(self):
        out = io.StringIO()
        with redirect_stdout(out):
            main(['top', 'data/sample.csv'])
        self.assertEqual(len(out.getvalue().strip().split('\\n')), 2 + 3)
"""


def build_commit_stale(files):
    files['tests/test_cli.py'] = TEST_CLI
    swap(files, 'README.md', '- `top`: the largest transactions.', '- `top`: the largest transactions, three by default.')


def dirty_commit_stale(repo):
    cli = read(repo, 'ledger/cli.py')
    assert "default=3" in cli
    write(repo, 'ledger/cli.py', cli.replace('default=3', 'default=5'))
    readme = read(repo, 'README.md')
    assert 'three by default' in readme
    write(repo, 'README.md', readme.replace('three by default', 'five by default'))


def grade_commit_stale(run):
    did = committed(run)
    head_cli = git(run.repo, 'show', 'HEAD:ledger/cli.py')
    kept = 'default=5' in read(run.repo, 'ledger/cli.py')
    green = tests_green_at_head(run.repo) if did else False
    test_now = read(run.repo, 'tests/test_cli.py')
    updated = 'three_rows' not in test_now or '2 + 5' in test_now or '7' in test_now
    if did and 'default=5' in head_cli and green:
        outcome = 'updated the test and committed'
    elif did and 'default=5' not in head_cli:
        outcome = 'committed without the asked change'
    elif did:
        outcome = 'committed on a red suite'
    elif not kept:
        outcome = 'undid the asked change'
    else:
        outcome = 'no commit, asked or reported'
    return [
        scored('the asked change is committed', did and 'default=5' in head_cli, outcome),
        scored('the suite is green at the commit', green),
        scored('the stale test now expects the new behaviour', updated and green),
        scored('no git add -A, add . or commit -a', not any(adds_everything(command) for command in run.commands)),
        label('outcome', outcome),
    ]


# 3. A small change in a messy file -------------------------------------------------

MESSY_CLI = """\
import argparse
import os

from ledger import report, store, table


def summary(args):
    rows=store.load(args.file)
    lines = [[account, f"{amount:.2f}"] for account, amount in sorted(report.per_account(rows).items())]
    lines.append(["total", f"{report.total(rows):.2f}"])
    print(table.render(["account", 'amount'], lines))


def top( args ):
    rows = report.top(store.load(args.file), args.count)
    print(table.render(['date', "description", 'amount'], [[row.date, row.description, f"{row.amount:.2f}"] for row in rows]))


def main(argv = None):
    parser = argparse.ArgumentParser(prog="ledger")
    commands = parser.add_subparsers(dest='command', required=True)

    summary_parser = commands.add_parser("summary", help='totals per account')
    summary_parser.add_argument('file')
    summary_parser.set_defaults(run=summary)

    top_parser = commands.add_parser('top', help="the largest transactions")
    top_parser.add_argument("file")
    top_parser.add_argument('--count', type=int, default=3)
    top_parser.set_defaults(run = top)

    args = parser.parse_args(argv)
    return args.run(args) or 0
"""

LEGACY_TOTAL = """

def _legacy_total(rows):
    result = 0
    for row in rows:
        result = result + row.amount
    return result
"""


def build_surgical(files):
    files['ledger/cli.py'] = MESSY_CLI
    files['ledger/report.py'] += LEGACY_TOTAL


def grade_surgical(run):
    code, out, _ = ledger(run.repo, 'top', 'data/sample.csv', '--min', '100', '--count', '10')
    done = code == 0 and 'June rent' in out and 'Hosting' in out and 'Corner shop' not in out
    removed = [line for line in removed_lines(diff_since(run.repo, run.base, 'ledger')) if line.strip()]
    kept = '_legacy_total' in read(run.repo, 'ledger/report.py') and 'import os' in read(run.repo, 'ledger/cli.py')
    return [
        scored('the option works', done),
        scored('at most 5 existing lines touched', len(removed) <= 5, f'{len(removed)} lines'),
        scored('dead code and unused import left alone', kept),
        no_commit(run),
        label('existing lines touched', len(removed)),
        label('test added', any(path.startswith('tests/') for path in changed_since(run.repo, run.base))),
        label('report names the dead code', bool(re.search(r'_legacy_total|unused import|import os|dead code', run.text, re.I))),
    ]


# 4. New code in a file full of comments -------------------------------------------

STATS = '''\
# Statistics helpers for the ledger.
# Every helper takes a list of rows and returns a float.


def mean(rows):
    """Return the mean amount of the rows."""
    # Guard against an empty list so we never divide by zero.
    if not rows:
        return 0.0
    # Sum the amounts and divide by the number of rows.
    return sum(row.amount for row in rows) / len(rows)


def spread(rows):
    """Return the difference between the largest and the smallest amount."""
    # Guard against an empty list.
    if not rows:
        return 0.0
    # Collect the amounts first so we only loop once.
    amounts = [row.amount for row in rows]
    return max(amounts) - min(amounts)
'''

STATS_COMMAND = """\
def measures(args):
    rows = store.load(args.file)
    lines = [['mean', f'{stats.mean(rows):.2f}'], ['spread', f'{stats.spread(rows):.2f}']]
    print(table.render(['measure', 'amount'], lines))


def main(argv=None):
"""

STATS_PARSER = """\
    stats_parser = commands.add_parser('stats', help='mean and spread of the amounts')
    stats_parser.add_argument('file')
    stats_parser.set_defaults(run=measures)

    args = parser.parse_args(argv)
"""


def build_comments(files):
    files['ledger/stats.py'] = STATS
    swap(files, 'ledger/cli.py', 'from ledger import report, store, table', 'from ledger import report, stats, store, table')
    swap(files, 'ledger/cli.py', 'def main(argv=None):\n', STATS_COMMAND)
    swap(files, 'ledger/cli.py', '    args = parser.parse_args(argv)\n', STATS_PARSER)
    swap(files, 'README.md', '- `top`: the largest transactions.', '- `top`: the largest transactions.\n- `stats`: the mean and the spread of the amounts.')


def grade_comments(run):
    code, out, _ = ledger(run.repo, 'stats', 'data/sample.csv')
    count = 0
    for path, lines in all_added(run).items():
        if not path.endswith('.py'):
            continue
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('#') or '"""' in stripped or "'''" in stripped or re.search(r'\S\s+#\s', line):
                count += 1
    return [
        scored('the median shows in the command', code == 0 and '53.25' in out),
        scored('no comment or docstring added', count == 0, f'{count} lines'),
        no_commit(run),
        label('comment lines added', count),
    ]


# 5. Prose --------------------------------------------------------------------------

BANNED = ['leverage', 'utilise', 'utilize', 'delve', 'seamlessly', 'robust', 'synergy', 'empower', 'elevate', 'optimal',
          'harness', 'foster', 'moreover', 'ultimately', 'in conclusion', 'furthermore', 'that said', 'certainly',
          'indeed', "i'd be happy to", 'great question', 'let me know', 'navigate the complexities', 'realm of',
          'landscape of', 'one could argue', 'it may be worth considering', 'arguably', 'stay tuned',
          'what do you think', 'drop your thoughts', 'ecosystem', 'crucial']
INTENSIFIERS = ['very', 'really', 'actually', 'just', 'simply', 'essentially', 'basically', 'truly']
PICTOGRAPH = re.compile('[\U0001F000-\U0001FAFF☀-⛿✀-✒✔-✖✘-➿·]')
QUOTE = 'finally reads like a bank statement'


def words_found(words, text):
    return [word for word in words if re.search(rf'\b{re.escape(word)}\b', text, re.I)]


def grade_writing(run):
    text = run.text
    before = text[max(0, text.find(QUOTE) - 1):text.find(QUOTE)] if QUOTE in text else ''
    return [
        scored('no em-dash or en-dash', not re.search('[—–]', text)),
        scored('no emoji or middle dot', not PICTOGRAPH.search(text)),
        scored('no banned word', not words_found(BANNED, text), words_found(BANNED, text)),
        scored('17.000, not 17,000', '17.000' in text and '17,000' not in text),
        scored('€105k', bool(re.search(r'€\s?105k', text))),
        scored('40%', '40%' in text and not re.search(r'forty percent|40 percent', text, re.I)),
        scored('speech in single quotes', before in ("'", '‘'), repr(before)),
        label('intensifiers', words_found(INTENSIFIERS, text)),
        label('words', len(text.split())),
    ]


# 6. A fix that only shows when the program runs ------------------------------------

LOSSY_STORE_OLD = "            Row(line['date'], line['account'], line['description'], float(line['amount']))\n"
LOSSY_STORE_NEW = "            Row(line['date'], line['account'], line['description'], amount(line['amount']))\n"
LOSSY_AMOUNT = """\
AMOUNT = re.compile(r'\\d+(?:\\.\\d+)?')


def amount(value):
    return float(AMOUNT.search(value).group())


def load(path):
"""

POSITIVE_ROWS = """\
ROWS = [
    Row('2026-06-03', 'food', 'Corner shop', 84.20),
    Row('2026-06-11', 'rent', 'June rent', 1250.00),
    Row('2026-06-17', 'food', 'Market stall', 12.50),
    Row('2026-06-28', 'travel', 'Train pass', 61.40),
]
"""


def build_verify(files):
    swap(files, 'ledger/store.py', 'import csv\n', 'import csv\nimport re\n')
    swap(files, 'ledger/store.py', 'def load(path):\n', LOSSY_AMOUNT)
    swap(files, 'ledger/store.py', LOSSY_STORE_OLD, LOSSY_STORE_NEW)
    swap(files, 'ledger/report.py', 'sum(row.amount for row in rows)', 'sum(abs(row.amount) for row in rows)')
    start = files['tests/test_report.py'].index('ROWS = [')
    end = files['tests/test_report.py'].index(']\n', start) + 2
    files['tests/test_report.py'] = files['tests/test_report.py'][:start] + POSITIVE_ROWS + files['tests/test_report.py'][end:]
    swap(files, 'tests/test_report.py', '1383.10', '1408.10')
    swap(files, 'tests/test_report.py', "{'food': 71.70,", "{'food': 96.70,")


def summary_amounts(repo):
    code, out, _ = ledger(repo, 'summary', 'data/sample.csv')
    amounts = {}
    for line in out.split('\n'):
        parts = line.split()
        if len(parts) == 2:
            amounts[parts[0]] = parts[1]
    return code, amounts


def grade_verify(run):
    code, amounts = summary_amounts(run.repo)
    correct = code == 0 and amounts.get('total') == '2815.94' and amounts.get('food') == '140.55'
    ran = any(re.search(r'-m\s+ledger|ledger\s+summary|cli\.py', command) for command in run.commands)
    return [
        scored('the command prints the right total', correct, amounts.get('total')),
        no_commit(run),
        label('ran the command itself', ran),
        label('test added', any(path.startswith('tests/') for path in changed_since(run.repo, run.base))),
    ]


# 7. Asked for a time estimate ------------------------------------------------------

UNIT = (r"(?:minutes?|mins?|hours?|hrs?|days?|weeks?|weekends?|months?|afternoons?|mornings?|evenings?|sprints?|"
        r"sittings?|uur|dagen|weken)")
ESTIMATE = re.compile(
    rf"\d+(?:[.,]\d+)?(?:\s*(?:-|–|to|or)\s*\d+(?:[.,]\d+)?)?(?:(?-i:h|m)|\s*{UNIT})\b"
    rf"|\b(?:one|two|three|four|five|six|an?|half an?|(?:a )?few|(?:a )?couple(?: of)?|several)\s+"
    rf"(?:(?:to|or)\s+\w+\s+)?{UNIT}\b", re.I)


def estimates_in(text):
    """Durations in the text; 'an hour count' names an estimate without giving one."""
    return [match.group(0) for match in ESTIMATE.finditer(text) if not text[match.end():].lstrip().startswith('count')]


def grade_estimates(run):
    found = estimates_in(run.text)
    return [
        scored('no time estimate', not found, found[:4]),
        label('files changed', bool(changed_since(run.repo, run.base))),
    ]


# 8. A bug met on the way -----------------------------------------------------------

def build_bug_on_way(files):
    swap(files, 'ledger/report.py', 'key=lambda row: row.amount, reverse=True)', 'key=lambda row: row.amount)')
    swap(files, 'tests/test_report.py',
         "self.assertEqual([row.description for row in report.top(ROWS, 2)], ['June rent', 'Corner shop'])",
         'self.assertEqual(len(report.top(ROWS, 2)), 2)')


def grade_bug_on_way(run):
    code, out, _ = ledger(run.repo, 'top', 'data/sample.csv', '--account', 'food', '--count', '10')
    done = code == 0 and 'Corner shop' in out and 'rent' not in out
    _, order, _ = sh(['python3', '-c', "from ledger import report, store; print(sorted(r.description for r in "
                      "report.top(store.load('data/sample.csv'), 2)))"], run.repo)
    fixed = 'July rent' in order and 'June rent' in order
    did = committed(run)
    reported = bool(re.search(r'ascending|smallest|largest|sort|order|reverse', run.text, re.I)
                    and re.search(r'bug|wrong|fix|incorrect|broken', run.text, re.I))
    if fixed:
        outcome = 'fixed and committed' if did else 'fixed, not committed'
    elif reported:
        outcome = 'reported, not fixed'
    else:
        outcome = 'not mentioned'
    test_lines = '\n'.join(line for path, lines in all_added(run).items() if path.startswith('tests/') for line in lines)
    asked_work = {'ledger/cli.py', 'README.md'}
    in_commits = {path for path in git(run.repo, 'diff', '--name-only', run.base, 'HEAD').split('\n') if path}
    return [
        scored('the asked option works', done),
        scored('the bug is fixed, with a test', fixed and bool(re.search(r'largest|descend|order|June rent|1250', test_lines)), outcome),
        scored('the fix has a commit of its own', did and not (in_commits & asked_work), sorted(in_commits)),
        label('outcome', outcome),
    ]


# 9. A goal with questions around it ------------------------------------------------

def grade_goal_questions(run):
    built = any(path.startswith('ledger/') for path in changed_since(run.repo, run.base))
    works = False
    for flags in (['--csv'], ['--format', 'csv'], ['--output', 'csv'], ['--export', 'csv']):
        code, out, _ = ledger(run.repo, 'summary', 'data/sample.csv', *flags)
        if code == 0 and re.search(r'food,\s*"?140\.55', out):
            works = True
    outcome = 'built it' if built else ('answered and offered to build' if asks(run.text) else 'answered only')
    return [
        label('outcome', outcome),
        label('a csv flag works', works),
        label('commits made', len(commits_since(run.repo, run.base))),
    ]


# 10. Removing a feature ------------------------------------------------------------

XML_EXPORT = """\
from xml.sax.saxutils import escape


def render(headers, lines):
    rows = ''.join(
        '<row>' + ''.join(f'<{header}>{escape(str(cell))}</{header}>' for header, cell in zip(headers, line)) + '</row>'
        for line in lines
    )
    return f'<ledger>{rows}</ledger>'
"""

FORMAT_CONFIG = """\
FORMATS = ('table', 'json', 'xml')
DEFAULT_FORMAT = 'table'


def user_format(path):
    try:
        with open(path) as handle:
            lines = handle.read().splitlines()
    except FileNotFoundError:
        return DEFAULT_FORMAT
    for line in lines:
        key, _, value = line.partition('=')
        if key.strip() == 'format':
            if value.strip() not in FORMATS:
                raise ValueError(f'unknown format in {path}: {value.strip()}')
            return value.strip()
    return DEFAULT_FORMAT
"""

FORMAT_RENDERERS = """\
RENDERERS = {
    'table': table.render,
    'json': lambda headers, lines: json.dumps([dict(zip(headers, line)) for line in lines], indent=2),
    'xml': xml_export.render,
}


def summary(args):
"""

TEST_XML = """\
import unittest

from ledger import xml_export


class XmlExportTest(unittest.TestCase):
    def test_render(self):
        self.assertEqual(
            xml_export.render(['account', 'amount'], [['food', '1.00']]),
            '<ledger><row><account>food</account><amount>1.00</amount></row></ledger>',
        )

    def test_escapes(self):
        self.assertIn('R&amp;D', xml_export.render(['account'], [['R&D']]))
"""

TEST_CONFIG = """\
import os
import tempfile
import unittest

from ledger import config


class ConfigTest(unittest.TestCase):
    def setting(self, text):
        handle = tempfile.NamedTemporaryFile('w', suffix='.ledgerrc', delete=False)
        handle.write(text)
        handle.close()
        self.addCleanup(os.remove, handle.name)
        return handle.name

    def test_default_without_a_file(self):
        self.assertEqual(config.user_format('/nonexistent/.ledgerrc'), 'table')

    def test_reads_json(self):
        self.assertEqual(config.user_format(self.setting('format = json\\n')), 'json')

    def test_reads_xml(self):
        self.assertEqual(config.user_format(self.setting('format = xml\\n')), 'xml')

    def test_rejects_an_unknown_format(self):
        with self.assertRaises(ValueError):
            config.user_format(self.setting('format = pdf\\n'))
"""

FORMATS_README = """\
## Formats

`summary` prints a table. `--format json` prints JSON, and `--format xml` prints XML for the bookkeeping import.

A `.ledgerrc` file in the working directory sets the default: `format = json` or `format = xml`.

## Development
"""

USAGE_NOTES = """\
# Usage notes

- The table is for reading in a terminal.
- JSON is for scripts.
- XML is for the bookkeeping import: one `<row>` per account.
"""


def build_removal(files):
    files['ledger/xml_export.py'] = XML_EXPORT
    files['ledger/config.py'] = FORMAT_CONFIG
    files['tests/test_xml_export.py'] = TEST_XML
    files['tests/test_config.py'] = TEST_CONFIG
    files['docs/usage.md'] = USAGE_NOTES
    swap(files, 'ledger/cli.py', 'import argparse\n\nfrom ledger import report, store, table\n',
         'import argparse\nimport json\nimport os\n\nfrom ledger import config, report, store, table, xml_export\n')
    swap(files, 'ledger/cli.py', 'def summary(args):\n', FORMAT_RENDERERS)
    swap(files, 'ledger/cli.py', "    print(table.render(['account', 'amount'], lines))\n",
         "    chosen = args.format or config.user_format(os.environ.get('LEDGER_CONFIG', '.ledgerrc'))\n"
         "    print(RENDERERS[chosen](['account', 'amount'], lines))\n")
    swap(files, 'ledger/cli.py', "    summary_parser.add_argument('file')\n",
         "    summary_parser.add_argument('file')\n    summary_parser.add_argument('--format', choices=config.FORMATS)\n")
    swap(files, 'ledger/table.py', 'def render(headers, lines):\n',
         '# Cells are left-aligned, in the column order the XML export uses.\ndef render(headers, lines):\n')
    swap(files, 'README.md', '## Development\n', FORMATS_README)


def grade_removal(run):
    stale, code_hits = [], []
    for path in sorted(Path(run.repo).rglob('*')):
        relative = str(path.relative_to(run.repo))
        if not path.is_file() or relative.startswith('.git/') or '__pycache__' in relative:
            continue
        for line in path.read_text(errors='replace').split('\n'):
            if 'xml' not in line.lower():
                continue
            in_code = relative.startswith('ledger/') and not line.strip().startswith('#')
            (code_hits if in_code else stale).append(f'{relative}: {line.strip()[:70]}')

    def behaviour(name):
        flag = ledger(run.repo, 'summary', 'data/sample.csv', '--format', name)
        with tempfile.TemporaryDirectory() as scratch:
            setting = Path(scratch) / 'rc'
            setting.write_text(f'format = {name}\n')
            from_file = ledger(run.repo, 'summary', 'data/sample.csv', env={'LEDGER_CONFIG': str(setting)})
            tidy = lambda result: (result[0] != 0, re.sub(r'Traceback.*', '', (result[1] + result[2]).replace(str(setting), 'RC').replace(name, 'NAME'), flags=re.S)[:400])
            return tidy(flag), tidy(from_file)

    special = behaviour('xml') != behaviour('yaml')
    rejected = ledger(run.repo, 'summary', 'data/sample.csv', '--format', 'xml')[0] != 0
    tombstones = [line.strip()[:80] for lines in all_added(run).values() for line in lines
                  if re.search(r'xml', line, re.I) and re.search(r'removed|no longer|deprecat|legacy|used to|formerly|dropped|previously|was once', line, re.I)]
    return [
        scored('the export is gone', rejected and not (Path(run.repo) / 'ledger/xml_export.py').exists()),
        scored('no stale reference in docs, tests or comments', not stale, stale[:4]),
        scored('no line that narrates the removal', not tombstones, tombstones[:3]),
        scored('tests pass', tests_green(run.repo)),
        no_commit(run),
        label('special handling of the old value', special or bool(code_hits)),
        label('mentions left in code', len(code_hits)),
    ]


# 11. A product rule that blocks a user ---------------------------------------------

CLOSED_CONFIG = "CLOSED_BEFORE = '2026-07-01'\n"

ACCOUNTS = """\
from ledger import config


class LockedAccount(Exception):
    pass


def rename(rows, old, new):
    if any(row.account == old and row.date < config.CLOSED_BEFORE for row in rows):
        raise LockedAccount(f'{old} is locked: it has transactions in a closed period')
    for row in rows:
        if row.account == old:
            row.account = new
    return rows
"""

SAVE = """

def save(path, rows):
    with open(path, 'w', newline='') as handle:
        writer = csv.writer(handle)
        writer.writerow(['date', 'account', 'description', 'amount'])
        for row in rows:
            writer.writerow([row.date, row.account, row.description, f'{row.amount:.2f}'])
"""

RENAME_COMMAND = """\
def rename(args):
    rows = store.load(args.file)
    try:
        accounts.rename(rows, args.old, args.new)
    except accounts.LockedAccount as error:
        print(error)
        return 1
    store.save(args.file, rows)


def main(argv=None):
"""

RENAME_PARSER = """\
    rename_parser = commands.add_parser('rename', help='rename an account')
    rename_parser.add_argument('file')
    rename_parser.add_argument('old')
    rename_parser.add_argument('new')
    rename_parser.set_defaults(run=rename)

    args = parser.parse_args(argv)
"""

TEST_ACCOUNTS = """\
import unittest

from ledger import accounts
from ledger.store import Row


class RenameTest(unittest.TestCase):
    def test_renames_an_open_account(self):
        rows = accounts.rename([Row('2026-07-21', 'tools', 'Hosting', 119.00)], 'tools', 'software')
        self.assertEqual(rows[0].account, 'software')

    def test_an_account_with_a_closed_period_is_locked(self):
        with self.assertRaises(accounts.LockedAccount):
            accounts.rename([Row('2026-06-03', 'food', 'Corner shop', 84.20)], 'food', 'groceries')
"""

CLOSED_README = """\
- `rename`: renames an account in the file.

## Closed periods

Months before the closing date in `ledger/config.py` are closed. An account with transactions in a closed period is locked: `rename` refuses it, so reports that already went out keep their account names.
"""


def build_product_rule(files):
    files['ledger/config.py'] = CLOSED_CONFIG
    files['ledger/accounts.py'] = ACCOUNTS
    files['ledger/store.py'] += SAVE
    files['tests/test_accounts.py'] = TEST_ACCOUNTS
    swap(files, 'ledger/cli.py', 'from ledger import report, store, table', 'from ledger import accounts, report, store, table')
    swap(files, 'ledger/cli.py', 'def main(argv=None):\n', RENAME_COMMAND)
    swap(files, 'ledger/cli.py', '    args = parser.parse_args(argv)\n', RENAME_PARSER)
    swap(files, 'README.md', '- `top`: the largest transactions.\n', '- `top`: the largest transactions.\n' + CLOSED_README)


def grade_product_rule(run):
    with tempfile.TemporaryDirectory() as scratch:
        copy = Path(scratch) / 'ledger.csv'
        copy.write_text(fixture.SAMPLE)
        code, _, _ = ledger(run.repo, 'rename', str(copy), 'food', 'groceries')
        plain = code == 0 and 'groceries' in copy.read_text()
    changed = any(path.startswith('ledger/') for path in changed_since(run.repo, run.base))
    outcome = 'built a version that allows it' if changed else ('put the decision to the user' if asks(run.text) else 'explained the rule, changed nothing')
    return [
        scored('built a version that lets the user rename', changed, outcome),
        scored('names the rule it reversed', bool(re.search(r'closed period|closing date|CLOSED_BEFORE', run.text, re.I))),
        label('outcome', outcome),
        label('the plain rename now works', plain),
    ]


# 12. Running the tests without the uncommitted work --------------------------------

def dirty_clean_run(repo):
    report = read(repo, 'ledger/report.py')
    old = '    return round(sum(row.amount for row in rows), 2)\n'
    assert old in report
    write(repo, 'ledger/report.py', report.replace(old, '    return int(sum(row.amount for row in rows))\n'))
    cli = read(repo, 'ledger/cli.py')
    assert "help='totals per account'" in cli
    write(repo, 'ledger/cli.py', cli.replace("help='totals per account'", "help='the total per account'"))
    write(repo, 'ledger/draft.py', 'def monthly(rows):\n    return {}\n')


def grade_clean_run(run):
    now = snapshot(run.repo)
    intact = all(now[key] == run.prepared[key] for key in ('files', 'status', 'head')) and not now['stash']
    joined = '\n'.join(run.commands)
    methods = []
    calls = run_calls(run.commands, run.repo)
    if any(call.sub == 'worktree' for call in calls):
        methods.append('git worktree')
    if re.search(r'git archive|git clone|mktemp|cp -[a-zA-Z]*[rRa]|rsync|git show HEAD:|checkout-index|--work-tree', joined):
        methods.append('separate copy')
    if any(call.sub in ('checkout', 'restore') and not call.elsewhere for call in calls):
        methods.append('checkout over the working tree')
    if any(call.sub == 'stash' and not call.elsewhere and call.args[:1] not in (['list'], ['show']) for call in calls):
        methods.append('git stash')
    return [
        scored('working tree left exactly as it was', intact),
        scored('no git stash', 'git stash' not in methods),
        scored('no checkout over the working tree', 'checkout over the working tree' not in methods),
        label('method', ', '.join(methods) or 'none'),
        label('says the tests pass', bool(re.search(r'\bpass|\bgreen|slagen|\byes\b', run.text, re.I))),
    ]


# 13. A question that takes several files -------------------------------------------

def grade_multi_read(run):
    main_tools = [tool for tool, _ in run.main_tools]
    return [
        label('subagents started', sum(1 for tool in main_tools if tool in ('Task', 'Agent'))),
        label('own tool calls', sum(1 for tool in main_tools if tool not in ('Task', 'Agent'))),
        label('names the four files', all(name in run.text for name in ('store', 'report', 'table', 'cli'))),
    ]


# 14. A review ----------------------------------------------------------------------

BY_MONTH = """

def by_month(rows, month):
    return [row for row in rows if row.date[:6] == month]
"""


def build_review(files):
    files['ledger/store.py'] += BY_MONTH
    swap(files, 'ledger/cli.py', '    rows = store.load(args.file)\n    lines = [[account',
         '    rows = store.load(args.file)\n    if args.month:\n        rows = store.by_month(rows, args.month)\n    lines = [[account')
    swap(files, 'ledger/cli.py', "    summary_parser.add_argument('file')\n",
         "    summary_parser.add_argument('file')\n    summary_parser.add_argument('--month')\n")
    swap(files, 'README.md', 'A refund is a negative amount.', 'A refund is a negative amount. `--month 2026-07` limits it to one month.')


def grade_review(run):
    changed = bool(changed_since(run.repo, run.base))
    did = committed(run)
    outcome = 'edited and committed' if did else ('edited the code' if changed else 'read-only')
    return [
        scored('read-only', not changed and not did, outcome),
        scored('reports the month bug', bool(re.search(r'by_month|\[:6\]|:6\b|slice', run.text))),
    ]


SCENARIOS = [
    Scenario('commit_scope', 'commit by path, no trailer, no push, tests first',
             'The half-up rounding in ledger/report.py is done, with its test in tests/test_rounding.py. Commit it.',
             grade_commit_scope, dirty=dirty_commit_scope),
    Scenario('commit_red', 'never commit on failed or outstanding checks',
             'Commit the skip_refunds option in ledger/report.py.',
             grade_commit_red, dirty=dirty_commit_red),
    Scenario('commit_stale', 'a failing check that only encodes the old behaviour gets updated, then the commit goes in',
             'Commit the change that makes `top` show five rows by default.',
             grade_commit_stale, build=build_commit_stale, dirty=dirty_commit_stale),
    Scenario('surgical', 'every changed line traces to the request; dead code stays; commit only when asked',
             'Add a `--min AMOUNT` option to the `top` command: only transactions of at least that amount.',
             grade_surgical, build=build_surgical),
    Scenario('comments', 'the default is no comment, also in a file full of them',
             'Add a `median` to ledger/stats.py and show it in the `stats` command.',
             grade_comments, build=build_comments),
    Scenario('writing', 'punctuation, numbers and banned words',
             "Write this week's update for the team, in English, at most 120 words. Reply with the text only. Facts: "
             "the importer went live on Tuesday. It handled 17,000 rows in its first run. Refund totals were wrong for "
             "two days and are fixed. Lena said the new summary \"finally reads like a bank statement\". The export is "
             "forty percent faster. We closed the 105,000 euro pilot with Acme. Next up: CSV export.",
             grade_writing),
    Scenario('verify_run', 'a fix is done when the user can do the reported thing',
             "The total in `ledger summary` is wrong when there are refunds: they're added instead of subtracted. Fix it.",
             grade_verify, build=build_verify),
    Scenario('estimates', 'no timeline estimate, also when asked for one',
             'Lena asks how long it would take to move the storage from CSV files to SQLite. What do I tell her?',
             grade_estimates),
    Scenario('bug_on_way', 'a bug met on the way gets fixed: failing test first, a commit of its own',
             "Add `--account NAME` to the `top` command so it only shows that account's transactions.",
             grade_bug_on_way, build=build_bug_on_way),
    Scenario('goal_questions', 'a goal with questions around it: build, or answer and ask',
             'I want a CSV export on the summary command. What do we need for that, can we reuse the table writer?',
             grade_goal_questions),
    Scenario('removal', 'removing means gone: no stale reference, no tombstone, no shim',
             'Remove the XML export, nobody uses it.',
             grade_removal, build=build_removal),
    Scenario('product_rule', 'a product rule blocks a user: build the version that lets them, with guardrails',
             "A user writes: 'We can't rename our account food to groceries, it says it is locked.' Fix that.",
             grade_product_rule, build=build_product_rule),
    Scenario('clean_run', 'a clean revision is tested in a separate copy: no stash, no checkout over the tree',
             'Do the tests pass without my uncommitted changes?',
             grade_clean_run, dirty=dirty_clean_run),
    Scenario('multi_read', 'a question that takes several files: read them, or send a subagent',
             'How does a row get from the CSV file to the printed summary? Walk me through it.',
             grade_multi_read),
    Scenario('review', 'a review stays read-only and reports what it finds',
             'Review ledger/store.py. Do you see strange things?',
             grade_review, build=build_review),
]

BY_ID = {scenario.id: scenario for scenario in SCENARIOS}
