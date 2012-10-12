#!/usr/bin/env python
from setuptools import setup

__doc__ = """
WiFi tools that could possibly work on a nice day, if you are lucky.
"""

install_requires = []
try:
    import argparse # NOQA
except:
    install_requires.append('argparse')

version = '0.0.1'

setup(
    name='wifi',
    version=version,
    description=__doc__,
    author='Rocky Meza, Gavin Wahl',
    author_email='rockymeza@gmail.com',
    packages=['wifi'],
    scripts=['bin/wifi'],
    platforms="Debian",
    license='BSD',
    install_requires=install_requires,
)
