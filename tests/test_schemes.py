from unittest import TestCase
import tempfile
import os

from wifi import Cell
from wifi.scheme import extract_schemes, Scheme
from wifi.exceptions import ConnectionError


NETWORK_INTERFACES_FILE = """
# This file describes the network interfaces available on your system
# and how to activate them. For more information, see interfaces(5).

# The loopback network interface
auto lo
iface lo inet loopback

# The primary network interface
allow-hotplug eth0
iface eth0 inet dhcp

iface wlan0-work inet dhcp
    wpa-ssid workwifi
    wireless-channel auto
    wpa-psk 1111111111111111111111111111111111111111111111111111111111111111

iface wlan0-coffee inet dhcp
    wireless-essid Coffee WiFi
    wireless-channel auto

iface wlan0-home inet dhcp
    wpa-ssid homewifi
    wpa-psk  2222222222222222222222222222222222222222222222222222222222222222
    wireless-channel auto

iface wlan0-coffee2 inet dhcp
    wireless-essid Coffee 2
    wireless-channel auto

iface wlan0-with-hyphen inet dhcp
    wireless-channel auto
    wireless-essid with-hyphen

iface xyz1-scheme inet dhcp
    wireless-channel auto
    wireless-essid scheme
"""


class TestSchemes(TestCase):
    def setUp(self):
        self.tempfile, interfaces = tempfile.mkstemp()

        with open(interfaces, 'w') as f:
            f.write(NETWORK_INTERFACES_FILE)

        self.Scheme = Scheme.for_file(interfaces)

    def tearDown(self):
        os.remove(self.Scheme.interfaces)

    def test_scheme_extraction(self):
        work, coffee, home, coffee2 = list(extract_schemes(NETWORK_INTERFACES_FILE))[:4]

        assert work.name == 'work'
        assert work.options['wpa-ssid'] == 'workwifi'

        assert coffee.name == 'coffee'
        assert coffee.options['wireless-essid'] == 'Coffee WiFi'

    def test_with_hyphen(self):
        with_hyphen = self.Scheme.find('wlan0', 'with-hyphen')
        assert with_hyphen.options['wireless-essid'] == 'with-hyphen'

    def test_with_different_interface(self):
        assert self.Scheme.find('xyz1', 'scheme')

    def test_str(self):
        scheme = self.Scheme('wlan0', 'test')
        assert str(scheme) == 'iface wlan0-test inet dhcp\n'

        scheme = self.Scheme('wlan0', 'test', {
            'wpa-ssid': 'workwifi',
        })

        self.assertEqual(str(scheme), 'iface wlan0-test inet dhcp\n    wpa-ssid workwifi\n')

    def test_find(self):
        work = self.Scheme.find('wlan0', 'work')

        assert work.options['wpa-ssid'] == 'workwifi'

    def test_delete(self):
        work = self.Scheme.find('wlan0', 'work')
        work.delete()
        self.assertIsNone(self.Scheme.find('wlan0', 'work'))
        assert self.Scheme.find('wlan0', 'coffee')

    def test_save(self):
        scheme = self.Scheme('wlan0', 'test')
        scheme.save()

        assert self.Scheme.find('wlan0', 'test')


class TestActivation(TestCase):
    def test_successful_connection(self):
        scheme = Scheme('wlan0', 'test')
        connection = scheme.parse_ifup_output(SUCCESSFUL_IFUP_OUTPUT)
        self.assertEqual(connection.scheme, scheme)
        self.assertEqual(connection.ip_address, '192.168.1.113')

    def test_failed_connection(self):
        scheme = Scheme('wlan0', 'test')
        self.assertRaises(ConnectionError, scheme.parse_ifup_output, FAILED_IFUP_OUTPUT)


class TestForCell(TestCase):
    def test_unencrypted(self):
        cell = Cell()
        cell.ssid = 'SSID'
        cell.encrypted = False

        scheme = Scheme.for_cell('wlan0', 'test', cell)

        self.assertEqual(scheme.options, {
            'wireless-essid': 'SSID',
            'wireless-channel': 'auto',
        })

    def test_wep_hex(self):
        cell = Cell()
        cell.ssid = 'SSID'
        cell.encrypted = True
        cell.encryption_type = 'wep'

        # hex key lengths: 10, 26, 32, 58
        hex_keys = ("01234567ab", "0123456789abc" * 2, "0123456789abcdef" * 2, "0123456789abc" * 2 + "0123456789abcdef" * 2)
        for key in hex_keys:
            scheme = Scheme.for_cell('wlan0', 'test', cell, key)

            self.assertEqual(scheme.options, {
                'wireless-essid': 'SSID',
                'wireless-key': key
            })

    def test_wep_ascii(self):
        cell = Cell()
        cell.ssid = 'SSID'
        cell.encrypted = True
        cell.encryption_type = 'wep'

        # ascii key lengths: 5, 13, 16, 29
        ascii_keys = ('a' * 5, 'a' * 13, 'a' * 16, 'a' * 29)
        for key in ascii_keys:
            scheme = Scheme.for_cell('wlan0', 'test', cell, key)

            self.assertEqual(scheme.options, {
                'wireless-essid': 'SSID',
                'wireless-key': 's:' + key
            })

    def test_wpa2(self):
        cell = Cell()
        cell.ssid = 'SSID'
        cell.encrypted = True
        cell.encryption_type = 'wpa2'

        scheme = Scheme.for_cell('wlan0', 'test', cell, b'passkey')

        self.assertEqual(scheme.options, {
            'wpa-ssid': 'SSID',
            'wpa-psk': 'ea1548d4e8850c8d94c5ef9ed6fe483981b64c1436952cb1bf80c08a68cdc763',
            'wireless-channel': 'auto',
        })

    def test_wpa(self):
        cell = Cell()
        cell.ssid = 'SSID'
        cell.encrypted = True
        cell.encryption_type = 'wpa'

        scheme = Scheme.for_cell('wlan0', 'test', cell, 'passkey')

        self.assertEqual(scheme.options, {
            'wpa-ssid': 'SSID',
            'wpa-psk': 'ea1548d4e8850c8d94c5ef9ed6fe483981b64c1436952cb1bf80c08a68cdc763',
            'wireless-channel': 'auto',
        })



SUCCESSFUL_IFDOWN_OUTPUT = """Internet Systems Consortium DHCP Client 4.2.4
Copyright 2004-2012 Internet Systems Consortium.
All rights reserved.
For info, please visit https://www.isc.org/software/dhcp/

Listening on LPF/wlan0/9c:4e:36:5d:2c:64
Sending on   LPF/wlan0/9c:4e:36:5d:2c:64
Sending on   Socket/fallback
DHCPRELEASE on wlan0 to 192.168.1.1 port 67
"""

SUCCESSFUL_IFUP_OUTPUT = """Internet Systems Consortium DHCP Client 4.2.4
Copyright 2004-2012 Internet Systems Consortium.
All rights reserved.
For info, please visit https://www.isc.org/software/dhcp/

Listening on LPF/wlan0/9c:4e:36:5d:2c:64
Sending on   LPF/wlan0/9c:4e:36:5d:2c:64
Sending on   Socket/fallback
DHCPDISCOVER on wlan0 to 255.255.255.255 port 67 interval 4
DHCPDISCOVER on wlan0 to 255.255.255.255 port 67 interval 8
DHCPREQUEST on wlan0 to 255.255.255.255 port 67
DHCPOFFER from 192.168.1.1
DHCPACK from 192.168.1.1
bound to 192.168.1.113 -- renewal in 2776 seconds.
"""

FAILED_IFUP_OUTPUT = """Internet Systems Consortium DHCP Client 4.2.4
Copyright 2004-2012 Internet Systems Consortium.
All rights reserved.
For info, please visit https://www.isc.org/software/dhcp/

Listening on LPF/wlan0/9c:4e:36:5d:2c:64
Sending on   LPF/wlan0/9c:4e:36:5d:2c:64
Sending on   Socket/fallback
DHCPDISCOVER on wlan0 to 255.255.255.255 port 67 interval 5
DHCPDISCOVER on wlan0 to 255.255.255.255 port 67 interval 8
DHCPDISCOVER on wlan0 to 255.255.255.255 port 67 interval 18
DHCPDISCOVER on wlan0 to 255.255.255.255 port 67 interval 18
DHCPDISCOVER on wlan0 to 255.255.255.255 port 67 interval 12
No DHCPOFFERS received.
No working leases in persistent database - sleeping.
"""
