#!/usr/bin/env python3
import argparse
from contextlib import ExitStack
import os
import sys
import subprocess
import threading
from borg.locking import ExclusiveLock as BorgLock
from borg.logger import setup_logging as setup_borg_logging
from borg.repository import Repository as BorgRepository

def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--timeout', type=int, default=3600, help='timeout to acquire a borg lock, defaults to %(default)d')
    parser.add_argument('-r', '--repositories', nargs='*')
    parser.add_argument('--sleep', type=int, default=5, help='sleep seconds when attempting to acquire lock, defaults to %(default)d')

    parser.add_argument('--no-repo-check', default=False, action='store_true')

    parser.add_argument('command', nargs='+', help='Command to run. Prefix with the argument "--" to avoid conflicts')
    args = parser.parse_args()

    for repo in args.repositories:
        if not BorgRepository.is_repository(repo) and not args.no_repo_check:
            raise Exception(f'Error: {repo} is not a Borg repository.')

    paths = [os.path.join(path, 'lock.exclusive') for path in args.repositories]

    locks = [BorgLock(path, args.timeout, args.sleep) for path in paths]

    with ExitStack() as stack:
        lock_threads = []
        for lock in locks:
            tlock = lambda: stack.enter_context(lock)
            t = threading.Thread(target=tlock)
            lock_threads.append(t)
            t.start()

        for t in lock_threads:
            t.join()

        p = subprocess.Popen(args.command, stdin=sys.stdin)
        p.communicate()
        return p.returncode


if __name__ == '__main__':
    main(sys.argv)
