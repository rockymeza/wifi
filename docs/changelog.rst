Changelog
=========

0.3.1
-----
:release-date: 2014-02-10

- Scheme.activate was failing on a TypeError in Python3

0.3.0
-----
:release-date: 2014-02-09

- Scheme.activate now throws a ConnectionError if activation failed (#17 - thanks alexykot)
- Cell.all now throws an InterfaceError if scanning failed (#18 - thanks alexykot)
- Better error message when scheme isn't found (#19 - thanks gavinwahl)
- Added ability to delete schemes (#20 - thanks spektom)
- Added the --file option (#21)
- Scheme.activate returns a Connection object (#22)
- Added the autoconnect command (#23)
- Fixed parsing error missing channel (#24 - thanks LiorKirsch)
- Fixed relative signal return as zero (#25 - thanks LiorKirsch)
- Relative signals are now converted to dBm (#26 - thanks LiorKirsch)
- Various codebase cleanup (#27 - thanks ramnes)
- Added support for WPA Version 1 (#28 - thanks LiorKirsch)
- Fixed Python3 support for WPA/PBKDF2

0.2.2
-----
:release-date: 2013-12-25

- Fixed relative signal parsing bug (#12 - thanks alexykot)

0.2.1
-----
:release-date: 2013-11-22

- Fixed print_table str/int bug (#13 - thanks DanLipsitt)

0.2.0
-----
:release-date: 2013-09-27

- Added support for WEP
- Fixed bug related to very short SSIDs
- Fixed bug related to numeric passkeys

0.1.1
-----
:release-date: 2013-05-26

- Updated setup.py to actually install the bash completion script
