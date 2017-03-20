wifi, a Python interface
========================

**Note:** This project is unmaintained. For more information, please visit the
GitHub page.

----

Wifi provides a set of tools for configuring and connecting to WiFi networks on Linux systems.
Using this library, you can discover networks, connect to them, save your configurations, and much, much more.

The original impetus for creating this library was my frustration with with connecting to the Internet using NetworkManager and wicd.
It is very much for computer programmers, not so much for normal computer users.
Wifi is built on top the old technologies of the `/etc/network/interfaces` file and `ifup` and `ifdown`.
It is inspired by `ifscheme`.

The library also comes with an executable that you can use to manage your WiFi connections.
Wifi currently supports the following encryption types:

-  No encryption
-  WEP
-  WPA2

If you need support for other network types, please file a bug on GitHub and we'll definitely try to get to it.
Patches, of course, are always welcome.


Installation
------------

Wifi is available for installation on PyPI::

    $ pip install wifi

This will install the :doc:`the wifi command <wifi_command>`, a Python library for discovering and connecting to wifi networks, and a bash completion file for the wifi command.

On some systems, the wifi command name is already used, and installing wifi will cause issues with the system.
In those cases you can override the command name that is installed::

    $ WIFI_CLI_NAME=cool-wifi pip install wifi

`The wifi executable <wifi_command>` will instead be named `cool-wifi`.

If you only want the Python library and don't care about the CLI, you can also disable it::

    $ WIFI_INSTALL_CLI=False pip install wifi

There will be no extra executable installed, but the wifi CLI will still be available using this invocation style::

    $ python -m wifi


Documentation
-------------

.. toctree::
    :maxdepth: 2

    wifi_command
    scanning
    changelog

Contributing
------------

The (very little) development for wifi happens on GitHub.
If you ever run into issues with wifi, please don't hesitate to open an issue.
Pull requests are welcome.
