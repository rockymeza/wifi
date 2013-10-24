# -*- coding: utf8 -*-
from __future__ import unicode_literals

from unittest import TestCase

try:
    from io import StringIO
except ImportError:  # Python < 3
    from StringIO import StringIO

from wifi.utils import print_table, match


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
