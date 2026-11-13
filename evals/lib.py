"""Shared helpers: an isolated git, running the fixture's code, and reading what a run attempted."""
import hashlib
import os
import re
import shlex
import subprocess
import tempfile
from pathlib import Path
from typing import NamedTuple

HERE = Path(__file__).resolve().parent

GIT_ENV = {
    'GIT_CONFIG_GLOBAL': str(HERE / 'gitconfig'),
    'GIT_CONFIG_NOSYSTEM': '1',
    'GIT_TERMINAL_PROMPT': '0',
}


def tool_env():
    env = {key: os.environ[key] for key in ('HOME', 'PATH', 'USER', 'TMPDIR') if key in os.environ}
    return {**env, **GIT_ENV, 'LANG': 'en_US.UTF-8', 'PYTHONDONTWRITEBYTECODE': '1'}


def sh(args, cwd, timeout=60, env=None):
    done = subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=timeout, env={**tool_env(), **(env or {})})
    return done.returncode, done.stdout, done.stderr


def git(repo, *args):
    code, out, err = sh(['git', *args], repo)
    if code:
        raise RuntimeError(f'git {" ".join(args)} failed in {repo}: {err.strip()}')
    return out


def tests_green(directory):
    code, _, _ = sh(['python3', '-m', 'unittest', '-q'], directory, timeout=120)
    return code == 0


def tests_green_at_head(repo):
    with tempfile.TemporaryDirectory() as scratch:
        archive = subprocess.run(['git', 'archive', 'HEAD'], cwd=repo, capture_output=True, env=tool_env())
        subprocess.run(['tar', '-x', '-C', scratch], input=archive.stdout, check=True)
        return tests_green(scratch)


def ledger(repo, *args, env=None):
    """Run the fixture's CLI; returns (exit code, stdout, stderr)."""
    return sh(['python3', '-m', 'ledger', *args], repo, timeout=30, env=env)


def snapshot(repo):
    """Content hash of every file outside .git, plus git's own view of the tree."""
    files = {}
    for path in sorted(Path(repo).rglob('*')):
        relative = path.relative_to(repo)
        if path.is_file() and relative.parts[0] != '.git' and '__pycache__' not in relative.parts:
            files[str(relative)] = hashlib.sha256(path.read_bytes()).hexdigest()
    return {
        'files': files,
        'status': git(repo, 'status', '--porcelain'),
        'head': git(repo, 'rev-parse', 'HEAD').strip(),
        'stash': git(repo, 'stash', 'list'),
    }


# What a run attempted -------------------------------------------------------

SEPARATORS = re.compile(r'(&&|\|\||[;|\n()])')
ASSIGNMENT = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*=')
PREFIXES = {'if', 'then', 'else', 'elif', 'while', 'until', 'do', '!', '{', 'time', 'nohup', 'nice', 'timeout', 'xargs',
            'command', 'exec', 'sudo', 'env', 'rtk', 'proxy'}
SHELLS = {'bash', 'sh', 'zsh'}
OUTSIDE = Path('/outside-the-repo')


class Call(NamedTuple):
    sub: str
    args: list
    elsewhere: bool = False


def simple_commands(command):
    """Every simple command in a shell line as a token list, in order, without keywords and launchers.

    The script of `bash -c '...'` is opened and read the same way. A subshell shows as ['('] and [')'].
    """
    found = []
    for segment in SEPARATORS.split(command):
        if segment in ('(', ')'):
            found.append([segment])
            continue
        try:
            tokens = shlex.split(segment)
        except ValueError:
            tokens = [token.strip('"\'') for token in segment.split()]
        launched = False
        while tokens and (ASSIGNMENT.match(tokens[0]) or tokens[0] in PREFIXES
                          or (launched and (tokens[0].startswith('-') or re.fullmatch(r'\d+(\.\d+)?[smhd]?', tokens[0])))):
            launched = launched or tokens[0] in PREFIXES
            tokens = tokens[1:]
        if not tokens or SEPARATORS.fullmatch(segment):
            continue
        if os.path.basename(tokens[0]) in SHELLS and '-c' in tokens[1:]:
            found.extend(simple_commands(' '.join(tokens[tokens.index('-c') + 1:])))
        else:
            found.append(tokens)
    return found


def parse_git(tokens):
    """(subcommand, arguments, -C directories in order, --work-tree or None) for a git command, else None."""
    if os.path.basename(tokens[0]) != 'git':
        return None
    rest, changes, work_tree = tokens[1:], [], None
    while rest and rest[0].startswith('-'):
        option, _, value = rest[0].partition('=')
        takes_next = rest[0] in ('-C', '-c', '--git-dir', '--work-tree')
        value = value or (rest[1] if takes_next and len(rest) > 1 else '')
        if option == '-C':
            changes.append(value)
        elif option == '--work-tree':
            work_tree = value
        rest = rest[2:] if takes_next else rest[1:]
    return (rest[0], rest[1:], changes, work_tree) if rest else None


def git_calls(command):
    """Every git invocation in a shell line. Use run_calls() to learn where each one ran."""
    parsed = (parse_git(tokens) for tokens in simple_commands(command) if tokens[0] not in ('(', ')'))
    return [Call(found[0], found[1]) for found in parsed if found]


def shell_variables(command):
    """Variables a command line assigns to a path it can name: a literal path, or a fresh mktemp directory."""
    variables = {}
    for name, value in re.findall(r'\b([A-Za-z_]\w*)=("?\$\(mktemp[^)]*\)"?|[^\s;&|()]+)', command):
        if 'mktemp' in value:
            variables[name] = OUTSIDE
        elif '$' not in value and '`' not in value:
            variables[name] = Path(value.strip('"\''))
    return variables


def locate(target, cwd, variables):
    """The directory a path argument names, or None when the command line doesn't say."""
    variable = re.fullmatch(r'\$\{?(\w+)\}?', target)
    if variable:
        value = variables.get(variable.group(1))
        return value if value is None or value.is_absolute() else Path(os.path.normpath(cwd / value))
    if target.startswith(('$', '~', '-')) or not target:
        return None
    return Path(os.path.normpath(cwd / target))


def run_calls(commands, repo):
    """Every git call of a run, in order. `elsewhere` is set only when the call provably ran outside `repo`.

    The working directory is followed through each command line and its subshells. Between commands it carries
    over only while it is inside the repo, as the harness resets a shell that ended elsewhere. Files land in
    `--work-tree`, or else in the directory after `-C`; `--git-dir` moves no files. A target the command line
    doesn't name counts as the repo.
    """
    repo = Path(os.path.normpath(repo))
    outside = lambda path: path is not None and repo != path and repo not in path.parents
    cwd, calls = repo, []
    for command in commands:
        cwd = repo if outside(cwd) else cwd
        variables, stack = shell_variables(command), []
        for tokens in simple_commands(command):
            if tokens == ['(']:
                stack.append(cwd)
            elif tokens == [')']:
                cwd = stack.pop() if stack else cwd
            elif tokens[0] == 'cd' and len(tokens) > 1:
                cwd = locate(tokens[1], cwd, variables) or repo
            else:
                found = parse_git(tokens)
                if found:
                    where = cwd
                    for change in found[2]:
                        where = locate(change, where, variables) or repo
                    if found[3] is not None:
                        where = locate(found[3], where, variables) or repo
                    calls.append(Call(found[0], found[1], outside(where)))
    return calls


def adds_everything(command):
    for call in git_calls(command):
        if call.sub == 'add' and any(arg in ('-A', '--all', '.', './', '-u', '--update', ':/', '*') for arg in call.args):
            return True
        if call.sub == 'commit' and any(arg == '--all' or re.fullmatch(r'-[a-zA-Z]*a[a-zA-Z]*', arg) for arg in call.args):
            return True
    return False


def uses_git(command, subcommand):
    return any(call.sub == subcommand for call in git_calls(command))


def runs_tests(tokens):
    name = os.path.basename(tokens[0])
    if name.startswith('python') and '-m' in tokens[:-1]:
        return tokens[tokens.index('-m') + 1] in ('unittest', 'pytest')
    return name == 'pytest'


def tests_before_commit(commands):
    """True when a test run comes before the first `git commit`, counted per simple command."""
    steps = [tokens for command in commands for tokens in simple_commands(command)]
    first_test = next((index for index, tokens in enumerate(steps) if runs_tests(tokens)), None)
    first_commit = next((index for index, tokens in enumerate(steps)
                         if os.path.basename(tokens[0]) == 'git' and uses_git(' '.join(map(shlex.quote, tokens)), 'commit')), None)
    return first_test is not None and (first_commit is None or first_test < first_commit)


def commits_since(repo, base):
    return [line for line in git(repo, 'rev-list', f'{base}..HEAD').split() if line]


def changed_since(repo, base):
    """Paths that differ between `base` and the working tree, untracked files included."""
    tracked = git(repo, 'diff', '--name-only', base).split('\n')
    untracked = git(repo, 'ls-files', '--others', '--exclude-standard').split('\n')
    return sorted({path for path in tracked + untracked if path})


def diff_since(repo, base, *paths):
    return git(repo, 'diff', base, '--', *paths) if paths else git(repo, 'diff', base)


def added_lines(diff):
    return [line[1:] for line in diff.split('\n') if line.startswith('+') and not line.startswith('+++')]


def removed_lines(diff):
    return [line[1:] for line in diff.split('\n') if line.startswith('-') and not line.startswith('---')]


def untracked_text(repo):
    """Contents of untracked files, which `git diff` leaves out."""
    paths = [path for path in git(repo, 'ls-files', '--others', '--exclude-standard').split('\n') if path]
    return {path: (Path(repo) / path).read_text(errors='replace') for path in paths}
