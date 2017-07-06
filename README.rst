**Note:** This project is unmaintained. While I would love to keep up the
development on this project, it is difficult for me for several reasons:

1.  I don't have enough time.

2.  I switched to Fedora and the corresponding scripts to manage WiFi are
    completely different. I was looking into re-writing the library in order to
    support more than just Debian based architectures, but it was too involved.

If anybody wants to take over the development of WiFi, please contact me. You
can find my email in the commit message.

----

wifi
----

Wifi provides a command line wrapper for iwlist and /etc/network/interfaces
that makes it easier to connect the WiFi networks from the command line.  The
wifi command is also implemented as a library that can be used from Python.

::

    # pip install wifi
    # wifi --help


.. image:: https://travis-ci.org/melvyn-sopacua/wifi.png?branch=master
   :target: https://travis-ci.org/melvyn-sopacua/wifi

The documentation for wifi lives at https://wifi.readthedocs.org/en/latest/.
