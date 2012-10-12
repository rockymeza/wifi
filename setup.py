#!/usr/bin/env python
from setuptools import setup
import os

__doc__ = """
WiFi tools that could possibly work on a nice day, if you are lucky.
"""


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


install_requires = []
try:
    import argparse # NOQA
except:
    install_requires.append('argparse')

version = '0.0.1'

setup(
    name='wifi',
    version=version,
    author='Rocky Meza, Gavin Wahl',
    author_email='rockymeza@gmail.com',
    description=__doc__,
    long_description=read('README.rst'),
    packages=['wifi'],
    scripts=['bin/wifi'],
    platforms="Debian",
    license='BSD',
    install_requires=install_requires,
    classifiers = [
        "License :: OSI Approved :: BSD License",
        "Topic :: System :: Networking",
        "Operating System :: POSIX :: Linux",
        "Environment :: Console",
    ],
)
