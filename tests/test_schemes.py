from unittest import TestCase
import tempfile

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
    wpa-ssid workwifi
    wpa-psk  1111111111111111111111111111111111111111111111111111111111111111
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
        self.tempfile, interfaces = tempfile.mkstemp()

        with open(interfaces, 'w') as f:
            f.write(NETWORK_INTERFACES_FILE)

        self.Scheme = Scheme.for_file(interfaces)

    def test_scheme_extraction(self):
        work, coffee, home, coffee2 = extract_schemes(NETWORK_INTERFACES_FILE)

        assert work.name == 'work'
        assert work.options['wpa-ssid'] == 'workwifi'

        assert coffee.name == 'coffee'
        assert coffee.options['wireless-essid'] == 'Coffee WiFi'

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

    def test_save(self):
        scheme = self.Scheme('wlan0', 'test')
        scheme.save()

        assert self.Scheme.find('wlan0', 'test')
