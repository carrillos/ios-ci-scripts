"""Workflow-facing release validation. No mutation; remote-head only reads Git."""
import argparse
import importlib.util
from pathlib import Path
import subprocess
import sys

spec = importlib.util.spec_from_file_location('release_git', Path(__file__).with_name('release-git.py'))
adapter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adapter)


def remote_head(repo, ref, expected):
    repo.commit(expected)
    if not ref.startswith(('refs/heads/', 'refs/pull/')):
        raise ValueError('expected a full branch or pull-request head ref')
    repo.git('check-ref-format', ref)
    rows = repo.git('ls-remote', '--exit-code', 'origin', ref).decode().splitlines()
    if rows != [expected + '\t' + ref]:
        raise ValueError('PR head moved or disappeared; retry on the current head')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', default='.')
    commands = parser.add_subparsers(dest='command', required=True)
    inspect = commands.add_parser('inspect')
    inspect.add_argument('--base', required=True)
    inspect.add_argument('--head', required=True)
    inspect.add_argument('--project', required=True)
    inspect.add_argument('--scope', action='append', required=True)
    inspect.add_argument('--read-only', action='store_true')
    check = commands.add_parser('remote-head')
    check.add_argument('--ref', required=True)
    check.add_argument('--expected', required=True)
    args = parser.parse_args(argv)
    repo = adapter.Repository(args.repo)
    if args.command == 'remote-head':
        remote_head(repo, args.ref, args.expected)
    else:
        print(repo.inspect(args.base, args.head, args.project, args.scope,
                           writable=not args.read_only))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        # Git stderr may contain remote configuration; report no credentials.
        message = 'Git operation failed; retry after checking repository access' if isinstance(
            error, subprocess.CalledProcessError) else str(error)
        print('release validation failed: ' + message, file=sys.stderr)
        sys.exit(2)
