wifi, a Python interface
========================

Wifi provides a set of tools for configuring and connecting to WiFi networks on Linux systems.
Using this library, you can discover networks, connect to them, save your configurations, and much, much more.

The original impetus for creating this library was my frustration with with connecting to the Internet using NetworkManager and wicd.
It is very much for computer programmers, not so much for normal computer users.
Wifi is built on top the old technologies of the `/etc/network/interfaces` file and `ifup` and `ifdown`.
It is inspired by `ifscheme`.

The library also comes with an executable that you can use to manage your WiFi connections.

Contents:

.. toctree::
   :maxdepth: 2

   wifi_command
   scanning



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
