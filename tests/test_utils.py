# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import sys
from unittest import TestCase

from wifi.utils import print_table, match, db2dbm, PrivilegedCommand

try:
    from io import StringIO
except ImportError:  # Python < 3
    from StringIO import StringIO

try:
    from wifi.subprocess_compat import TimeoutExpired
except ImportError:
    class TimeoutExpired(Exception):
        pass

print_table_in = [
    ['1', '123456789', 'hello'],
    ['2344566', 'góodbŷe', 'foo']
]
print_table_out = """
1        123456789  hello
2344566  góodbŷe    foo
""".lstrip()


class PrintTableTest(TestCase):
    def test_lengths_formatted_correctly(self):
        stdout = StringIO()
        print_table(print_table_in, file=stdout)
        self.assertEqual(stdout.getvalue(), print_table_out)

    def test_no_failure_with_non_strs(self):
        stdout = StringIO()
        print_table([[1], ['2']], file=stdout)
        self.assertEqual(stdout.getvalue(), '1\n2\n')


class FuzzyMatchTest(TestCase):
    def test_match(self):
        assert match('f', 'foo') > 0
        assert match('x', 'foo') == 0
        assert match('hl', 'hello') > 0
        assert match('hel', 'hello') > match('ho', 'hello')


class db2dbMTest(TestCase):
    def test_db2dbm(self):
        self.assertEqual(db2dbm(-10), -100)
        self.assertEqual(db2dbm(0), -100)
        self.assertEqual(db2dbm(1), -99)
        self.assertEqual(db2dbm(2), -99)
        self.assertEqual(db2dbm(50), -75)
        self.assertEqual(db2dbm(99), -50)
        self.assertEqual(db2dbm(100), -50)
        self.assertEqual(db2dbm(101), -50)
        self.assertEqual(db2dbm(200), -50)


class PrivilegedCommandTest(TestCase):
    askpass_program = os.path.join(os.path.dirname(__file__), 'bin', 'ppass.py')

    def test_use_sudo(self):
        command = PrivilegedCommand('/bin/echo', 'Hello World!',
                                    use_sudo=False)
        self.assertEqual(command.use_sudo, False)
        self.assertEqual('Hello World!', command().decode('utf-8').strip())

    def test_timeout(self):
        if sys.version < '3':
            self.skipTest('Timeouts not supported on Python 2')
            return
        command = PrivilegedCommand('/bin/sleep', '1', timeout=0.25,
                                    use_sudo=False)
        with self.assertRaises(TimeoutExpired):
            command()

    def test_askpass(self):
        if not os.getenv('WIFI_TEST_SUDO_PASSWORD', False):
            self.skipTest('SKIP: No sudo password set in environment')
            return
        command = PrivilegedCommand('/bin/echo', 'Hello World!',
                                    askpass=self.askpass_program)
        self.assertEqual(command.use_sudo, True)
        self.assertEqual('Hello World!', command().decode('utf-8').strip())
