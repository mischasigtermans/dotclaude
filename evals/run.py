#!/usr/bin/env python3
"""Run the scenarios against CLAUDE.md, grade each run, and report.

  run.py probe                      check that a run sees only the variant under test
  run.py selftest                   build every fixture and grade it untouched; no model runs
  run.py run --batch NAME [--arms none,current] [--scenarios a,b] [--reps 3]
  run.py report --batch NAME [--batch OTHER]

Arms: `none` is no instructions, `current` is this repo's CLAUDE.md with
rules/orchestration.md, and any other name reads evals/variants/<name>.md.

A run gets a fresh copy of the fixture in a temp directory outside your home
folder. The variant sits one level above the repo as CLAUDE.md, and the run
loads project settings only, so your own instructions, rules, hooks, plugins
and MCP servers stay out of it.
"""
import argparse
import collections
import concurrent.futures
import json
import os
import random
import secrets
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))

import fixture  # noqa: E402
from lib import GIT_ENV, git, snapshot, tests_green  # noqa: E402
from scenarios import BY_ID, SCENARIOS, Scenario  # noqa: E402

CLAUDE = os.environ.get('CLAUDE_BIN') or shutil.which('claude')
WORK = Path(tempfile.gettempdir()).resolve() / 'claude-md-evals'
DISALLOWED = ('WebFetch WebSearch CronCreate CronDelete CronList RemoteTrigger PushNotification SendMessage ListAgents '
              'EnterWorktree ExitWorktree DesignSync ScheduleWakeup Monitor Workflow NotebookEdit')
TIMEOUT = 900
LOCK = threading.Lock()
CANARY = 'ZEBRAFISH-41'


@dataclass
class Run:
    repo: Path
    remote: Path
    base: str
    prepared: dict
    commands: list = field(default_factory=list)
    main_tools: list = field(default_factory=list)
    text: str = ''


def variant(arm):
    if arm == 'none':
        return None
    if arm == 'current':
        return (ROOT / 'CLAUDE.md').read_text() + '\n' + (ROOT / 'rules' / 'orchestration.md').read_text()
    return (HERE / 'variants' / f'{arm}.md').read_text()


def prepare(scenario, instructions, directory):
    """Build the fixture for one run; returns the Run with its prepared state."""
    repo, remote = directory / 'ledger', directory / 'origin.git'
    files = fixture.base()
    if scenario.build:
        scenario.build(files)
    for path, content in files.items():
        target = repo / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)
    git(repo, 'init', '-q', '-b', 'main')
    git(repo, 'add', '--', *files)
    git(repo, 'commit', '-q', '-m', 'Ledger reports from a CSV file')
    git(directory, 'init', '-q', '--bare', str(remote))
    git(repo, 'remote', 'add', 'origin', str(remote))
    git(repo, 'push', '-q', '-u', 'origin', 'main')
    base = git(repo, 'rev-parse', 'HEAD').strip()
    if scenario.dirty:
        scenario.dirty(repo)
    if instructions is not None:
        (directory / 'CLAUDE.md').write_text(instructions)
    return Run(repo=repo, remote=remote, base=base, prepared=snapshot(repo))


def child_env(directory):
    keep = {key: os.environ[key] for key in ('HOME', 'USER', 'TMPDIR', 'CLAUDE_CONFIG_DIR') if key in os.environ}
    return {
        **keep, **GIT_ENV,
        'PATH': f"{HERE / 'shims'}:{os.environ['PATH']}",
        'LANG': 'en_US.UTF-8', 'TERM': 'dumb', 'PYTHONDONTWRITEBYTECODE': '1',
        'CLAUDE_CODE_DISABLE_AUTO_MEMORY': '1',
        'AB_SHIM_LOG': str(directory / 'shims.log'),
    }


def execute(run, prompt, directory, model, effort):
    command = [
        CLAUDE, '-p', prompt,
        '--setting-sources', 'project,local', '--strict-mcp-config', '--no-session-persistence',
        '--disable-slash-commands', '--permission-mode', 'auto', '--settings', '{"autoMemoryEnabled": false}',
        '--disallowedTools', DISALLOWED, '--model', model, '--effort', effort, '--max-budget-usd', '3',
        '--output-format', 'stream-json', '--verbose',
    ]
    stream = directory / 'stream.jsonl'
    started = time.time()
    with open(stream, 'w') as out, open(directory / 'stderr.txt', 'w') as err:
        try:
            exit_code = subprocess.run(command, cwd=run.repo, stdin=subprocess.DEVNULL, stdout=out, stderr=err,
                                       env=child_env(directory), timeout=TIMEOUT).returncode
        except subprocess.TimeoutExpired:
            exit_code = 'timeout'
    return read_stream(run, stream, {'exit': exit_code, 'seconds': round(time.time() - started)})


def read_stream(run, stream, meta):
    """Fill the Run with what was attempted and said; returns the run's meta."""
    for line in open(stream, errors='replace'):
        try:
            row = json.loads(line)
        except ValueError:
            continue
        kind = row.get('type')
        if kind == 'assistant':
            for part in (row.get('message') or {}).get('content') or []:
                if isinstance(part, dict) and part.get('type') == 'tool_use':
                    tool, given = part.get('name', ''), part.get('input') or {}
                    if not row.get('parent_tool_use_id'):
                        run.main_tools.append((tool, given))
                    if tool == 'Bash':
                        run.commands.append(str(given.get('command', '')))
        elif kind == 'rate_limit_event':
            info = row.get('rate_limit_info') or {}
            if info.get('utilization') is not None:
                meta['utilization'] = info['utilization']
        elif kind == 'result':
            run.text = row.get('result') or ''
            meta.update(cost=row.get('total_cost_usd'), turns=row.get('num_turns'), subtype=row.get('subtype'),
                        error=row.get('is_error'))
    meta['valid'] = meta.get('exit') == 0 and meta.get('subtype') == 'success' and not meta.get('error')
    return meta


def one(batch, scenario_id, arm, rep, model, effort):
    scenario = BY_ID[scenario_id]
    directory = WORK / batch / secrets.token_hex(4)
    directory.mkdir(parents=True)
    run = prepare(scenario, variant(arm), directory)
    meta = execute(run, scenario.prompt, directory, model, effort)
    try:
        checks = scenario.grade(run)
    except Exception as error:  # a grader that crashes must not lose the run
        checks, meta['grader_error'] = [], repr(error)
    record = {'scenario': scenario_id, 'arm': arm, 'rep': rep, 'dir': str(directory), 'meta': meta, 'checks': checks,
              'text': run.text[:6000], 'commands': run.commands}
    with LOCK:
        with open(HERE / 'results' / f'{batch}.jsonl', 'a') as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + '\n')
        scored = [check for check in checks if check['kind'] == 'scored']
        verdict = 'PASS' if scored and all(check['ok'] for check in scored) else ('FAIL' if scored else '----')
        print(f"{scenario_id:15} {arm:8} #{rep} {verdict} ${meta.get('cost') or 0:.2f} {meta.get('seconds')}s "
              f"valid={meta.get('valid')} weekly={meta.get('utilization')}", flush=True)
    return record


def load(batch):
    path = HERE / 'results' / f'{batch}.jsonl'
    return [json.loads(line) for line in open(path)] if path.exists() else []


def preflight():
    if not CLAUDE:
        sys.exit('claude is not on PATH; set CLAUDE_BIN to the binary')
    if Path.home().resolve() in WORK.parents:
        sys.exit(f'{WORK} is inside your home folder, so runs would load your own CLAUDE.md; set TMPDIR elsewhere')
    (HERE / 'results').mkdir(exist_ok=True)


def command_run(args):
    preflight()
    done = {(r['scenario'], r['arm'], r['rep']) for r in load(args.batch) if r['meta'].get('valid')}
    scenario_ids = args.scenarios.split(',') if args.scenarios else [scenario.id for scenario in SCENARIOS]
    jobs = [(scenario_id, arm, rep) for scenario_id in scenario_ids for arm in args.arms.split(',')
            for rep in range(1, args.reps + 1) if (scenario_id, arm, rep) not in done]
    random.Random(args.batch).shuffle(jobs)
    print(f'{len(jobs)} runs, {args.workers} at a time, model {args.model}, effort {args.effort}', flush=True)
    spent, stop, queue, pending = 0.0, False, collections.deque(jobs), set()
    with concurrent.futures.ThreadPoolExecutor(args.workers) as pool:
        while queue or pending:
            while queue and len(pending) < args.workers and not stop:
                pending.add(pool.submit(one, args.batch, *queue.popleft(), args.model, args.effort))
            if not pending:
                break
            finished, pending = concurrent.futures.wait(pending, return_when=concurrent.futures.FIRST_COMPLETED)
            for future in finished:
                meta = future.result()['meta']
                spent += meta.get('cost') or 0
                stop = stop or spent >= args.max_usd or (meta.get('utilization') or 0) >= args.stop_at
    print(f'spent ${spent:.2f}; {len(queue)} runs not started' + (' (ceiling reached)' if stop else ''), flush=True)


def command_report(args):
    records = [record for batch in args.batch for record in load(batch) if record['meta'].get('valid')]
    arms = sorted({record['arm'] for record in records}, key=lambda arm: (arm != 'none', arm))
    print(f"{len(records)} valid runs; arms: {', '.join(arms)}\n")
    for scenario in SCENARIOS:
        mine = [record for record in records if record['scenario'] == scenario.id]
        if not mine:
            continue
        print(f'## {scenario.id}: {scenario.rules}')
        names = list(dict.fromkeys((check['kind'], check['name']) for record in mine for check in record['checks']))
        for arm in arms:
            runs = [record for record in mine if record['arm'] == arm]
            scored = [[check for check in record['checks'] if check['kind'] == 'scored'] for record in runs]
            passed = sum(1 for checks in scored if checks and all(check['ok'] for check in checks))
            cost = sum(record['meta'].get('cost') or 0 for record in runs) / max(1, len(runs))
            print(f'  {arm:8} n={len(runs)}' + (f'  pass {passed}/{len(runs)}' if any(scored) else '') + f'  avg ${cost:.2f}')
            for kind, name in names:
                values = [check for record in runs for check in record['checks'] if check['name'] == name]
                if kind == 'scored':
                    failed = [check['detail'] for check in values if not check['ok']]
                    if failed:
                        print(f'        ✗ {name}: failed {len(failed)}/{len(values)} {[d for d in failed if d][:2]}')
                else:
                    counts = collections.Counter(json.dumps(check['value'], ensure_ascii=False) for check in values)
                    print(f'        {name}: ' + ', '.join(f'{value} ×{count}' for value, count in counts.most_common()))
        print()
    for arm in arms:
        runs = [record for record in records if record['arm'] == arm]
        print(f"{arm:8} runs={len(runs)} ${sum(record['meta'].get('cost') or 0 for record in runs):.2f}")


def command_selftest(args):
    for scenario in SCENARIOS:
        with tempfile.TemporaryDirectory() as scratch:
            run = prepare(scenario, None, Path(scratch))
            checks = scenario.grade(run)
            scored = [check for check in checks if check['kind'] == 'scored']
            print(f"{scenario.id:15} tests {'green' if tests_green(run.repo) else 'RED  '} "
                  f"untouched: {sum(check['ok'] for check in scored)}/{len(scored)} scored ok; "
                  + '; '.join(f"{check['name']}={check['value']}" for check in checks if check['kind'] == 'label'))


def command_probe(args):
    """One cheap run that must name the variant file, and no other instruction file."""
    preflight()
    directory = WORK / 'probe' / secrets.token_hex(4)
    directory.mkdir(parents=True)
    question = ('List the absolute path of every instruction or memory file whose contents you were given (CLAUDE.md, '
                'rules, MEMORY.md), one per line, then the canary word if one of them states it. Nothing else.')
    run = prepare(Scenario('probe', '', question, None), f'# Probe\n\nThe canary word is {CANARY}.\n', directory)
    execute(run, question, directory, 'haiku', 'low')
    paths = [line.strip() for line in run.text.split('\n') if line.strip().startswith('/')]
    isolated = paths == [str(directory / 'CLAUDE.md')] and CANARY in run.text
    print(run.text)
    print('isolated: only the variant was loaded' if isolated else 'NOT ISOLATED: a run sees other instruction files')
    sys.exit(0 if isolated else 1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('probe').set_defaults(func=command_probe)
    commands.add_parser('selftest').set_defaults(func=command_selftest)
    run_parser = commands.add_parser('run')
    run_parser.add_argument('--batch', required=True)
    run_parser.add_argument('--scenarios')
    run_parser.add_argument('--arms', default='none,current')
    run_parser.add_argument('--reps', type=int, default=3)
    run_parser.add_argument('--workers', type=int, default=4)
    run_parser.add_argument('--model', default='opus')
    run_parser.add_argument('--effort', default='high')
    run_parser.add_argument('--max-usd', type=float, default=30, help='stop starting runs once this much is spent')
    run_parser.add_argument('--stop-at', type=float, default=0.8, help='stop once the weekly limit is this full (0-1)')
    run_parser.set_defaults(func=command_run)
    report_parser = commands.add_parser('report')
    report_parser.add_argument('--batch', action='append', required=True)
    report_parser.set_defaults(func=command_report)
    parsed = parser.parse_args()
    parsed.func(parsed)
