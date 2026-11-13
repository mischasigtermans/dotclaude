"""The small project every scenario starts from: a CSV ledger with a CLI.

`base()` returns {path: content}. A scenario edits that dict before the first
commit, then may leave uncommitted changes on top.
"""

GITIGNORE = '__pycache__/\n*.pyc\n'

SAMPLE = """\
date,account,description,amount
2026-06-03,food,Corner shop,84.20
2026-06-11,rent,June rent,1250.00
2026-06-17,food,Refund corner shop,-12.50
2026-06-28,travel,Train pass,61.40
2026-07-02,food,Market stall,45.10
2026-07-09,rent,July rent,1250.00
2026-07-15,travel,Refund train pass,-20.00
2026-07-21,tools,Hosting,119.00
2026-07-30,food,Bakery,23.75
2026-08-04,tools,Domain renewal,14.99
"""

README = """\
# Ledger

Reads a CSV of transactions and prints reports.

## Usage

```sh
python3 -m ledger summary data/sample.csv
python3 -m ledger top data/sample.csv --count 3
```

- `summary`: the total per account, and the overall total. A refund is a negative amount.
- `top`: the largest transactions.

## Development

Run the tests with `python3 -m unittest`.
"""

MAIN = """\
from ledger.cli import main

raise SystemExit(main())
"""

STORE = """\
import csv
from dataclasses import dataclass


@dataclass
class Row:
    date: str
    account: str
    description: str
    amount: float


def load(path):
    with open(path, newline='') as handle:
        return [
            Row(line['date'], line['account'], line['description'], float(line['amount']))
            for line in csv.DictReader(handle)
        ]


def by_account(rows, account):
    return [row for row in rows if row.account == account]
"""

REPORT = """\
def total(rows):
    return round(sum(row.amount for row in rows), 2)


def top(rows, count):
    return sorted(rows, key=lambda row: row.amount, reverse=True)[:count]


def per_account(rows):
    totals = {}
    for row in rows:
        totals[row.account] = round(totals.get(row.account, 0) + row.amount, 2)
    return totals
"""

TABLE = """\
def render(headers, lines):
    widths = [max(len(str(cell)) for cell in column) for column in zip(headers, *lines)]

    def line(cells):
        return '  '.join(str(cell).ljust(width) for cell, width in zip(cells, widths)).rstrip()

    return '\\n'.join([line(headers), line(['-' * width for width in widths]), *map(line, lines)])
"""

CLI = """\
import argparse

from ledger import report, store, table


def summary(args):
    rows = store.load(args.file)
    lines = [[account, f'{amount:.2f}'] for account, amount in sorted(report.per_account(rows).items())]
    lines.append(['total', f'{report.total(rows):.2f}'])
    print(table.render(['account', 'amount'], lines))


def top(args):
    rows = report.top(store.load(args.file), args.count)
    print(table.render(['date', 'description', 'amount'], [[row.date, row.description, f'{row.amount:.2f}'] for row in rows]))


def main(argv=None):
    parser = argparse.ArgumentParser(prog='ledger')
    commands = parser.add_subparsers(dest='command', required=True)

    summary_parser = commands.add_parser('summary', help='totals per account')
    summary_parser.add_argument('file')
    summary_parser.set_defaults(run=summary)

    top_parser = commands.add_parser('top', help='the largest transactions')
    top_parser.add_argument('file')
    top_parser.add_argument('--count', type=int, default=3)
    top_parser.set_defaults(run=top)

    args = parser.parse_args(argv)
    return args.run(args) or 0
"""

TEST_REPORT = """\
import unittest

from ledger import report
from ledger.store import Row

ROWS = [
    Row('2026-06-03', 'food', 'Corner shop', 84.20),
    Row('2026-06-11', 'rent', 'June rent', 1250.00),
    Row('2026-06-17', 'food', 'Refund corner shop', -12.50),
    Row('2026-06-28', 'travel', 'Train pass', 61.40),
]


class ReportTest(unittest.TestCase):
    def test_total(self):
        self.assertEqual(report.total(ROWS), 1383.10)

    def test_top(self):
        self.assertEqual([row.description for row in report.top(ROWS, 2)], ['June rent', 'Corner shop'])

    def test_per_account(self):
        self.assertEqual(report.per_account(ROWS), {'food': 71.70, 'rent': 1250.00, 'travel': 61.40})


if __name__ == '__main__':
    unittest.main()
"""


def base():
    return {
        '.gitignore': GITIGNORE,
        'README.md': README,
        'data/sample.csv': SAMPLE,
        'ledger/__init__.py': '',
        'ledger/__main__.py': MAIN,
        'ledger/cli.py': CLI,
        'ledger/report.py': REPORT,
        'ledger/store.py': STORE,
        'ledger/table.py': TABLE,
        'tests/__init__.py': '',
        'tests/test_report.py': TEST_REPORT,
    }


def swap(files, path, old, new, count=1):
    """Replace `old` with `new` in files[path]; fail loudly when it isn't there."""
    if files[path].count(old) < 1:
        raise AssertionError(f'{path}: text to replace not found: {old[:60]!r}')
    files[path] = files[path].replace(old, new, count)
