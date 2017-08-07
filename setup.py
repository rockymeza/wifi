#!/usr/bin/env python
import os
import sys

from setuptools import setup

__doc__ = """
Command line tool and library wrappers around iwlist and
/etc/network/interfaces.
"""


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


install_requires = [
    'setuptools',
    'pbkdf2',
]
try:
    import argparse
except ImportError:
    install_requires.append('argparse')
else:
    del argparse

version = '0.8.0rc1'

should_install_cli = os.environ.get('WIFI_INSTALL_CLI') not in ['False', '0']
command_name = os.environ.get('WIFI_CLI_NAME', 'pywifi')

if command_name == 'wifi.py':
    print(
        "Having a command name of wifi.py will result in a weird ImportError"
        " that doesn't seem possible to work around. Pretty much any other"
        " name seems to work though."
    )
    sys.exit(1)

entry_points = {}
data_files = []

if should_install_cli:
    entry_points['console_scripts'] = [
        '{command} = wifi.cli:main'.format(command=command_name),
    ]
    # make sure we actually have write access to the target folder and if not do
    # not include it in data_files.
    if os.access('/etc/bash_completion.d/', os.W_OK):
        data_files.append(
            ('/etc/bash_completion.d/', ['extras/wifi-completion.bash'])
        )
    else:
        print("Not installing bash completion because of lack of permissions.")

setup(
    name='wifi',
    version=version,
    author='Melvyn Sopacua, Rocky Meza, Gavin Wahl',
    author_email='melvyn@unikotec.com',
    description=__doc__,
    long_description='\n\n'.join([read('README.rst'), read('CHANGES.rst')]),
    packages=['wifi'],
    entry_points=entry_points,
    test_suite='tests',
    platforms=["Debian"],
    license='BSD',
    install_requires=install_requires,
    classifiers=[
        "License :: OSI Approved :: BSD License",
        "Topic :: System :: Networking",
        "Operating System :: POSIX :: Linux",
        "Environment :: Console",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
    ],
    data_files=data_files,
    zip_safe=False,
)
