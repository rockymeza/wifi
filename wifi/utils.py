from __future__ import print_function, unicode_literals, division

import logging
import os
import subprocess
import sys

from pbkdf2 import PBKDF2

if sys.version < '3':
    str = unicode

logger = logging.getLogger('wifi')
if os.getenv('WIFI_DEBUG', False):
    logger.setLevel(logging.DEBUG)


def match(needle, haystack):
    """
    Command-T-style string matching.
    """
    score = 1
    j = 0
    last_match = 0
    needle = needle.lower()
    haystack = haystack.lower()

    for c in needle:
        while j < len(haystack) and haystack[j] != c:
            j += 1
        if j >= len(haystack):
            return 0
        score += 1 / (last_match + 1.)
        last_match = j
        j += 1
    return score


def print_table(matrix, sep='  ', file=sys.stdout, *args, **kwargs):
    """
    Prints a left-aligned table of elements.
    """
    lengths = [max(map(len, map(str, column))) for column in zip(*matrix)]
    format = sep.join(
        '{{{0}:<{1}}}'.format(i, length) for i, length in enumerate(lengths))

    for row in matrix:
        print(format.format(*row).strip(), file=file, *args, **kwargs)


def db2dbm(quality):
    """
    Converts the Radio (Received) Signal Strength Indicator (in db) to a dBm
    value.  Please see http://stackoverflow.com/a/15798024/1013960
    """
    dbm = int((quality / 2) - 100)
    return min(max(dbm, -100), -50)


def ensure_file_exists(filename):
    """
    http://stackoverflow.com/a/12654798/1013960
    """
    if not os.path.exists(filename):
        open(filename, 'a').close()


def pass2psk(ssid, raw):
    # Note: this relies on the default being HMAC-SHA1.
    obj = PBKDF2(raw, ssid, iterations=4096)
    return obj.hexread(32)


class PrivilegedCommand(object):
    sudo_path = '/usr/bin/sudo'
    askpass_program = None
    env_path = '/usr/bin/env'
    _uid = None

    def __init__(self, cmd, *args, **kwargs):
        self.use_sudo = kwargs.pop('use_sudo', True)
        self.askpass_program = kwargs.pop('askpass', self.askpass_program)
        self.command = []
        if self.use_sudo:
            if self.askpass_program is not None:
                self.command.extend(
                    [self.env_path, 'SUDO_ASKPASS=' + self.askpass_program,
                     self.sudo, '--askpass']
                )
            else:
                self.command.append(self.sudo)
        self.command.append(cmd)
        self.command.extend(args)
        self.timeout = kwargs.pop('timeout', None)
        self.process_kwargs = kwargs

        super(PrivilegedCommand, self).__init__()

    def _get_kwargs(self):
        # If more is added to init that is always passed on to subprocess
        # add it here.
        # The dict shall always be literal and not cached, as a pristine copy
        # is needed, that isn't tainted by accessing `self.kwargs` or similar
        #  constructs.
        kwargs = self.process_kwargs
        if not sys.version < '3':
            kwargs['timeout'] = self.timeout
        logger.debug('Returning kwargs %r', kwargs)
        return kwargs

    @property
    def uid(self):
        if self._uid is None:
            self._uid = os.getuid()
        return self._uid

    @property
    def sudo(self):
        if self.uid > 0:
            return self.sudo_path
        return self.env_path

    def __call__(self, with_stderr=False):
        kwargs = self._get_kwargs()
        if with_stderr:
            kwargs['stderr'] = subprocess.STDOUT
        output = subprocess.check_output(self.command, **kwargs)
        logger.debug(
            'Got %d bytes for "%s"', len(output), ' '.join(self.command)
        )
        return output
