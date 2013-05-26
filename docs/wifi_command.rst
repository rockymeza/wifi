The wifi Command
================

This library comes with a command line program for managing and saving your WiFi connections.

Usage
^^^^^

::

    usage: wifi {scan,list,config,add,connect,init} ...

scan
----

Shows a list of available networks. ::

    usage: wifi scan

list
----

Shows a list of networks already configured. ::

    usage: wifi list

add, config
-----------

Prints or adds the configuration to connect to a new network. ::

    usage: wifi config SCHEME [SSID]
    usage: wifi add SCHEME [SSID]

    positional arguments:
      SCHEME      A memorable nickname for a wireless network. If SSID is not
                  provided, the network will be guessed using SCHEME.
      SSID        The SSID for the network to which you wish to connect. This is
                  fuzzy matched, so you don't have to be precise.

connect
-------

Connects to the network corresponding to SCHEME. ::

    usage: wifi connect SCHEME

    positional arguments:
      SCHEME      The nickname of the network to which you wish to connect.


Completion
^^^^^^^^^^

The wifi command also comes packaged with completion for bash.
If you want to write completion for your own shell, wifi provides an interface for extracting completion information.
Please see the ``wifi-completion.bash`` and ``bin/wifi`` files for more information.
