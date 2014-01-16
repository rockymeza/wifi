from unittest import TestCase
import tempfile
import os

from wifi.scheme import extract_schemes, Scheme


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
    wpa-psk 1111111111111111111111111111111111111111111111111111111111111111
    wpa-ssid workwifi
    wireless-channel auto

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
"""


class TestSchemes(TestCase):
    def setUp(self):
        self.tempfile, Scheme.interfaces = tempfile.mkstemp()

        with open(Scheme.interfaces, 'w') as f:
            f.write(NETWORK_INTERFACES_FILE)

    def tearDown(self):
        os.remove(Scheme.interfaces)

    def test_scheme_extraction(self):
        work, coffee, home, coffee2 = extract_schemes(NETWORK_INTERFACES_FILE)

        assert work.name == 'work'
        assert work.options['wpa-ssid'] == 'workwifi'

        assert coffee.name == 'coffee'
        assert coffee.options['wireless-essid'] == 'Coffee WiFi'

    def test_str(self):
        scheme = Scheme('wlan0', 'test')
        assert str(scheme) == 'iface wlan0-test inet dhcp\n'

        scheme = Scheme('wlan0', 'test', {
            'wpa-ssid': 'workwifi',
        })

        self.assertEqual(str(scheme), 'iface wlan0-test inet dhcp\n    wpa-ssid workwifi\n')

    def test_find(self):
        work = Scheme.find('wlan0', 'work')

        assert work.options['wpa-ssid'] == 'workwifi'

    def test_delete(self):
        work = Scheme.find('wlan0', 'work')
        work.delete()
        assert Scheme.find('wlan0', 'work') == None

    def test_save(self):
        scheme = Scheme('wlan0', 'test')
        scheme.save()

        assert Scheme.find('wlan0', 'test')
