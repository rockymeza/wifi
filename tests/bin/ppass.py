#!/usr/bin/env python
import os
import sys


def main():
    passwd = os.getenv('WIFI_TEST_SUDO_PASSWORD', False)
    if passwd:
        print(passwd)
    else:
        sys.exit(status=os.EX_USAGE)


if __name__ == '__main__':
    main()
