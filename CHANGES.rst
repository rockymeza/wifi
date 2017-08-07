Changelog
=========

0.8.0rc1
^^^^^^^^
:release-date: 2017-08-07

- Add support for sudo
- Change default command name to `pywifi`, to evade conflicts with other packages
- Add attribute `frequency_norm` which is the normalized frequency, aka frequency band
  as one would find on packaging of WiFi hardware. Only 2.4Ghz and 5Ghz bands are
  supported.
- Fix some typo's in this document and create some more (probably)

0.4.0
^^^^^
:release-date: 2017-07-17

- Internal release only
- Make the wifi command name configurable (#55 - thanks yourealwaysbe)
- Add a __main__.py so that wifi can be invoked using python -mwifi
- Fix argument parsing so that scan is the default argument even with options passed
- Add preliminary EAP support (#63 - thanks irgusite)
- Update test suite and overall PEP8 formatting
- Fix WPA detection
- Fix relative signal level parsing to not rely on stable dictionary order
- Centralize code to reformat a passphrase to a psk
- Add ability to generate a `wpa_supplicant` network configuration from a cell
- Add parsing for:
  - Group cipher
  - Pairwise ciphers
  - Authentication suites
  Please note that it's likely to be refactored into a separate object, as more then
  one of these triplets may exist for a given cell.
- Add logging

0.3.8
^^^^^
:release-date: 2016-03-11

- Parse noise level if available (#91 - thanks zgoda-mobica)

0.3.7
^^^^^
:release-date: 2016-03-11

- Fix bugs related to scheme parsing (#59, #42)

0.3.6
^^^^^
:release-date: 2016-02-11

- Set all attributes to None in Cell.__init__ (#88 - thanks stvad)

0.3.5
^^^^^
:release-date: 2016-01-24

- Better password handling (#62 - thanks foosel)
- Account for Cells with no SSID (#86 - thanks tlau)

0.3.4
^^^^^
:release-date: 2014-09-02

- Fixed installation missing some files (#48 - thanks luckydonald)

0.3.3
^^^^^
:release-date: 2014-08-31

- Check for write access for bashcompletion via os.access (#41, #47 - thanks foosel and jegger)
- Fixed scanning when quality is reported absolutely (#45 - jeromelebel)
- Fixed channel parsing (#33, #39 - thanks gavinwahl and qizha)

0.3.2
^^^^^
:release-date: 2014-07-26

- Only run if __name__ == '__main__' (#29 - thanks Jonwei)
- Try to connect to the nearest Access Point
- wifi scan was failing when Bit Rate was the last line of output (#42 - thanks jargij)
- Added documentation for signal and quality on Cell

0.3.1
^^^^^
:release-date: 2014-02-10

- Scheme.activate was failing on a TypeError in Python3

0.3.0
^^^^^
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
^^^^^
:release-date: 2013-12-25

- Fixed relative signal parsing bug (#12 - thanks alexykot)

0.2.1
^^^^^
:release-date: 2013-11-22

- Fixed print_table str/int bug (#13 - thanks DanLipsitt)

0.2.0
^^^^^
:release-date: 2013-09-27

- Added support for WEP
- Fixed bug related to very short SSIDs
- Fixed bug related to numeric passkeys

0.1.1
^^^^^
:release-date: 2013-05-26

- Updated setup.py to actually install the bash completion script
