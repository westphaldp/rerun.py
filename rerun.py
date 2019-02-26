#!/usr/bin/env python3

# This software may be modified and distributed under the terms
# of the MIT license.  See the LICENSE file for details.

import os
import sys
import time
from subprocess import Popen

def usage():
    use = f'''{sys.argv[0]} executable arguements -- files

executable - executable to monitor for changes and ensure running state
arguements - arguements passed to executable
files - files to monitor for changes
'''
    return use

if __name__ == '__main__':

    if len(sys.argv) < 2:
        print(usage())
        exit()

    args = []
    files = []
    
    if '--' in sys.argv:
        sep = sys.argv.index('--')
        args = sys.argv[1:sep]
        files = sys.argv[sep+1:]
    else:
        args = sys.argv[1:]

    files = args[0:1] + files

    print(f'Running \'{" ".join(args)}\' until killed, restarting if changes'
          f' in: {", ".join(files)}')

    try:
        proc = None
        last_change = 0
        newest_change = time.time()
        while True:
            if newest_change > last_change:
                print(f'\n(re)launching \'{" ".join(args)}\'')
                last_change = newest_change
                if proc and proc.poll() is None:
                    print('terminating old process')
                    proc.terminate()
                    try:
                        proc.communicate(timeout=5)
                    except TimeoutExpired:
                        proc.kill()
                # unexpected FileNotFoundError occasionally on the executable
                time.sleep(0.1)
                print('launching new process\n')
                proc = Popen(args, stdout=sys.stdout, stderr=sys.stderr)

            time.sleep(1)

            for f in files:
                # NOTE: Can throw the following on the file that was modified.
                #    'FileNotFoundError: [Errno 2] No such file or directory'
                try:
                    mtime = os.stat(f).st_mtime
                    if mtime > newest_change:
                        newest_change = mtime
                except FileNotFoundError:
                    pass

    except Exception as e:
        print('cleaning up')
        if proc and proc.poll():
            proc.terminate()
            try:
                proc.communicate(timeout=5)
            except TimeoutExpired:
                proc.kill()

        raise e
