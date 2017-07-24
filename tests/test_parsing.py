from unittest import TestCase

from wifi.exceptions import InterfaceError
from wifi.scan import Cell


class IWListParserTest(TestCase):
    def test_no_encryption(self):
        cell = Cell.from_string(IWLIST_SCAN_NO_ENCRYPTION)
        self.assertFalse(cell.encrypted)
        self.assertEqual('My Wireless Network', cell.ssid)
        self.assertEqual(-51, cell.signal)
        self.assertEqual('59/70', cell.quality)
        self.assertEqual('2.437 GHz', cell.frequency)
        self.assertEqual('Master', cell.mode)
        self.assertEqual(6, cell.channel)

    def test_wep(self):
        cell = Cell.from_string(IWLIST_SCAN_WEP)
        self.assertTrue(cell.encrypted)
        self.assertEqual('wep', cell.encryption_type)

    def test_wpa2(self):
        cell = Cell.from_string(IWLIST_SCAN_WPA2)
        self.assertTrue(cell.encrypted)
        self.assertEqual('wpa2', cell.encryption_type)

    def test_wpa_wpa2(self):
        cell = Cell.from_string(IWLIST_SCAN_WPA_WPA2)
        self.assertTrue(cell.encrypted)
        self.assertEqual('wpa/wpa2', cell.encryption_type)

    def test_wpa2_enterprise(self):
        cell = Cell.from_string(IWLIST_SCAN_WPA2_ENTERPRISE)
        self.assertTrue(cell.encrypted)
        self.assertEqual('wpa2-enterprise', cell.encryption_type)

    def test_wpa_enterprise(self):
        cell = Cell.from_string(IWLIST_SCAN_WPA_ENTERPRISE)
        self.assertTrue(cell.encrypted)
        self.assertEqual('wpa-enterprise', cell.encryption_type)

    def test_wpa1(self):
        cell = Cell.from_string(IWLIST_SCAN_WPA1)
        self.assertTrue(cell.encrypted)
        self.assertEqual('wpa', cell.encryption_type)

    def test_alternative_iwlist_output(self):
        # https://github.com/rockymeza/wifi/issues/12
        cell = Cell.from_string(ALTERNATIVE_OUTPUT)
        self.assertEqual('78/100', cell.quality)
        self.assertEqual(-92, cell.signal)

    def test_signal_level_out_of_sixty(self):
        cell = Cell.from_string(ALTERNATIVE_OUTPUT2)
        self.assertEqual(-71, cell.signal)

    def test_noname_cell(self):
        cell = Cell.from_string(NONAME_WIRELESS_NETWORK)
        self.assertEqual('', cell.ssid)

    def test_no_channel_output(self):
        cell = Cell.from_string(NO_CHANNEL_OUTPUT)
        self.assertEqual(11, cell.channel)

    def test_list_index_error(self):
        cell = Cell.from_string(LIST_INDEX_ERROR)

    def test_frequency_no_channel_output(self):
        cell = Cell.from_string(FREQUENCY_NO_CHANNEL_OUTPUT)
        self.assertEqual(149, cell.channel)

    def test_absolute_quality(self):
        # https://github.com/rockymeza/wifi/pull/45
        cell = Cell.from_string(ABSOLUTE_QUALITY)
        self.assertEqual('38/100', cell.quality)
        self.assertEqual(-92, cell.signal)

    def test_blank_ssid(self):
        cell = Cell.from_string(NO_SSID_AT_ALL)
        self.assertEqual(None, cell.ssid)

    def test_noise_no_data(self):
        cell = Cell.from_string(IWLIST_SCAN_NO_ENCRYPTION)
        self.assertEqual(None, cell.noise)

    def test_noise_data_present(self):
        cell = Cell.from_string(LIST_INDEX_ERROR)
        self.assertEqual(-92, cell.noise)

    def test_bssid(self):
        # This seems like a useless test, yet if bssid is refactored and not
        # in sync with address attribute, this will alert us.
        cell = Cell.from_string(ALTERNATIVE_OUTPUT)
        self.assertEqual(cell.address, cell.bssid)
        cell.bssid = 'AC:22:05:25:3B:6A'
        self.assertEqual('AC:22:05:25:3B:6A', cell.address)

    def test_pairwise_ciphers(self):
        cell = Cell.from_string(IWLIST_SCAN_WPA_WPA2_DUAL_CIPHERS)
        self.assertListEqual(['CCMP', 'TKIP'], cell.pairwise_ciphers)

    def test_group_cipher(self):
        cell = Cell.from_string(IWLIST_SCAN_WPA2)
        self.assertEqual('CCMP', cell.group_cipher)

    def test_normalized_frequency(self):
        cell = Cell.from_string(FREQUENCY_5G)
        self.assertEqual(cell.frequency_norm, '5Ghz')
        cell = Cell.from_string(IWLIST_SCAN_WPA2)
        self.assertEqual(cell.frequency_norm, '2.4Ghz')
        cell = Cell.from_string(FREQUENCY_UNSUPPORTED)
        self.assertIsNone(cell.frequency_norm)


class ScanningTest(TestCase):
    def test_scanning(self):
        self.assertRaises(InterfaceError, Cell.all, 'fake-interface')


class WpaSupCfgWriterTest(TestCase):
    def test_wpa1_psk(self):
        cell = Cell.from_string(IWLIST_SCAN_WPA1)
        self.assertEqual(WSCFG_WPA1, cell.gen_wpasup_cfg('supersecret'))

    def test_wpa2_psk(self):
        cell = Cell.from_string(IWLIST_SCAN_WPA2)
        self.assertEqual(WSCFG_WPA2, cell.gen_wpasup_cfg('supersecret'))

    def test_open_ap(self):
        cell = Cell.from_string(IWLIST_SCAN_NO_ENCRYPTION)
        self.assertEqual(WSCFG_OPEN, cell.gen_wpasup_cfg())

    def test_unimplemented(self):
        cell = Cell.from_string(IWLIST_SCAN_WPA_ENTERPRISE)
        with self.assertRaises(NotImplementedError):
            cell.gen_wpasup_cfg('supersecret')


IWLIST_SCAN_NO_ENCRYPTION = """Cell 02 - Address: 
                    Channel:6
                    Frequency:2.437 GHz (Channel 6)
                    Quality=59/70  Signal level=-51 dBm  
                    Encryption key:off
                    ESSID:"My Wireless Network"
                    Bit Rates:1 Mb/s; 2 Mb/s; 5.5 Mb/s; 11 Mb/s; 6 Mb/s
                              9 Mb/s; 12 Mb/s; 18 Mb/s
                    Bit Rates:24 Mb/s; 36 Mb/s; 48 Mb/s; 54 Mb/s
                    Mode:Master
                    Extra:tsf=00000079fc961317
                    Extra: Last beacon: 60ms ago
"""

IWLIST_SCAN_WEP = """Cell 01 - Address: 
                    Channel:6
                    Frequency:2.437 GHz (Channel 6)
                    Quality=36/70  Signal level=-74 dBm  
                    Encryption key:on
                    ESSID:"WEP Network"
                    Bit Rates:1 Mb/s; 2 Mb/s; 5.5 Mb/s; 11 Mb/s; 6 Mb/s
                              12 Mb/s; 24 Mb/s; 36 Mb/s
                    Bit Rates:9 Mb/s; 18 Mb/s; 48 Mb/s; 54 Mb/s
                    Mode:Master
                    Extra:tsf=00000022fa7f11cd
                    Extra: Last beacon: 60ms ago
"""

IWLIST_SCAN_WPA_WPA2 = """Cell 08 - Address: 
                    Channel:1
                    Frequency:2.412 GHz (Channel 1)
                    Quality=42/70  Signal level=-68 dBm  
                    Encryption key:on
                    ESSID:"WPA/WPA2 network"
                    Bit Rates:1 Mb/s; 2 Mb/s; 5.5 Mb/s; 11 Mb/s; 9 Mb/s
                              18 Mb/s; 36 Mb/s; 54 Mb/s
                    Bit Rates:6 Mb/s; 12 Mb/s; 24 Mb/s; 48 Mb/s
                    Mode:Master
                    Extra:tsf=000000029170ed29
                    Extra: Last beacon: 24ms ago
                    IE: WPA Version 1
                        Group Cipher : TKIP
                        Pairwise Ciphers (1) : TKIP
                        Authentication Suites (1) : PSK
                    IE: IEEE 802.11i/WPA2 Version 1
                        Group Cipher : TKIP
                        Pairwise Ciphers (1) : TKIP
                        Authentication Suites (1) : PSK
                    """
IWLIST_SCAN_WPA_WPA2_DUAL_CIPHERS = """Cell 03 - Address: 98:F5:37:59:55:EC
                    Channel:1
                    Frequency:2.412 GHz (Channel 1)
                    Quality=25/70  Signal level=-85 dBm
                    Encryption key:on
                    ESSID:"H220N5955EC"
                    Bit Rates:1 Mb/s; 2 Mb/s; 5.5 Mb/s; 11 Mb/s; 18 Mb/s
                              24 Mb/s; 36 Mb/s; 54 Mb/s
                    Bit Rates:6 Mb/s; 9 Mb/s; 12 Mb/s; 48 Mb/s
                    Mode:Master
                    Extra:tsf=0000000000000000
                    Extra: Last beacon: 70ms ago
                    IE: IEEE 802.11i/WPA2 Version 1
                        Group Cipher : TKIP
                        Pairwise Ciphers (2) : CCMP TKIP
                        Authentication Suites (1) : PSK
                    IE: WPA Version 1
                        Group Cipher : TKIP
                        Pairwise Ciphers (2) : CCMP TKIP
                        Authentication Suites (1) : PSK
"""
IWLIST_SCAN_WPA2 = """Cell 02 - Adress:
                    Channel:1
                    Frequency:2.412 GHz (Channel 1)
                    Quality=70/70  Signal level=-25 dBm
                    Encryption key:on
                    ESSID:"WPA2"
                    Bit Rates:1 Mb/s; 2 Mb/s; 5.5 Mb/s; 11 Mb/s
                    Bit Rates:6 Mb/s; 9 Mb/s; 12 Mb/s; 18 Mb/s; 24 Mb/s
                              36 Mb/s; 48 Mb/s; 54 Mb/s
                    Mode:Master
                    Extra:tsf=000001a12fade963
                    Extra: Last beacon: 10ms ago
                    IE: IEEE 802.11i/WPA2 Version 1
                        Group Cipher : CCMP
                        Pairwise Ciphers (1) : CCMP
                        Authentication Suites (1) : PSK
"""

IWLIST_SCAN_WPA2_ENTERPRISE = """Cell 04 - Address: 
                    Channel:1
                    Frequency:2.412 GHz (Channel 1)
                    Quality=42/70  Signal level=-68 dBm
                    Encryption key:on
                    ESSID:"WPA2-Enterprise"
                    Bit Rates:1 Mb/s; 2 Mb/s; 5.5 Mb/s; 11 Mb/s; 18 Mb/s
                              24 Mb/s; 36 Mb/s; 54 Mb/s
                    Bit Rates:6 Mb/s; 9 Mb/s; 12 Mb/s; 48 Mb/s
                    Mode:Master
                    Extra:tsf=0000000744e298fd
                    Extra: Last beacon: 10ms ago
                    IE: IEEE 802.11i/WPA2 Version 1
                        Group Cipher : TKIP
                        Pairwise Ciphers (2) : CCMP TKIP
                        Authentication Suites (1) : 802.1x
"""

IWLIST_SCAN_WPA_ENTERPRISE = """Cell 04 - Address: 
                    Channel:1
                    Frequency:2.412 GHz (Channel 1)
                    Quality=42/70  Signal level=-68 dBm
                    Encryption key:on
                    ESSID:"WPA2-Enterprise"
                    Bit Rates:1 Mb/s; 2 Mb/s; 5.5 Mb/s; 11 Mb/s; 18 Mb/s
                              24 Mb/s; 36 Mb/s; 54 Mb/s
                    Bit Rates:6 Mb/s; 9 Mb/s; 12 Mb/s; 48 Mb/s
                    Mode:Master
                    Extra:tsf=0000000744e298fd
                    Extra: Last beacon: 10ms ago
                    IE: IEEE 802.11i/WPA
                        Group Cipher : TKIP
                        Pairwise Ciphers (2) : CCMP TKIP
                        Authentication Suites (1) : 802.1x
"""

IWLIST_SCAN_WPA1 = """Cell 01 - Address: 
                    ESSID: WPA1
                    Protocol:IEEE 802.11bg
                    Mode:Master
                    Frequency:2.457 GHz (Channel 10)
                    Encryption key:on
                    Bit Rates:54 Mb/s
                    Extra:wpa_ie=dd160050f20101000050f20201000050f20201000050f202
                    IE: WPA Version 1
                        Group Cipher : TKIP
                        Pairwise Ciphers (1) : TKIP
                        Authentication Suites (1) : PSK
                    Quality=100/100  Signal level=74/100  
"""

ALTERNATIVE_OUTPUT = """Cell 06 - Address: F2:23:DB:A3:3B:A0
                    ESSID:"Antons iPhone"
                    Protocol:IEEE 802.11g
                    Mode:Master
                    Frequency:2.412 GHz (Channel 1)
                    Encryption key:on
                    Bit Rates:54 Mb/s
                    Extra:rsn_ie=30140100000fac040100000fac040100000fac020c00
                    IE: IEEE 802.11i/WPA2 Version 1
                        Group Cipher : CCMP
                        Pairwise Ciphers (1) : CCMP
                        Authentication Suites (1) : PSK
                    Quality=78/100  Signal level=16/100
"""

ALTERNATIVE_OUTPUT2 = """Cell 06 - Address: F2:23:DB:A3:3B:A0
                    ESSID:"Antons iPhone"
                    Protocol:IEEE 802.11g
                    Mode:Master
                    Frequency:2.412 GHz (Channel 1)
                    Encryption key:on
                    Bit Rates:54 Mb/s
                    Extra:rsn_ie=30140100000fac040100000fac040100000fac020c00
                    IE: IEEE 802.11i/WPA2 Version 1
                        Group Cipher : CCMP
                        Pairwise Ciphers (1) : CCMP
                        Authentication Suites (1) : PSK
                    Quality=78/100  Signal level=35/60
"""

NONAME_WIRELESS_NETWORK = """Cell 01 - Address: A4:56:30:E8:97:F0
                    ESSID:""
                    Protocol:IEEE 802.11gn
                    Mode:Master
                    Frequency:2.437 GHz (Channel 6)
                    Encryption key:on
                    Bit Rates:144 Mb/s
                    Extra:wpa_ie=dd1c0050f20101000050f20202000050f2020050f20401000050f2020000
                    IE: WPA Version 1
                        Group Cipher : TKIP
                        Pairwise Ciphers (2) : TKIP CCMP
                        Authentication Suites (1) : PSK
                    Extra:rsn_ie=30180100000fac020200000fac02000fac040100000fac022800
                    IE: IEEE 802.11i/WPA2 Version 1
                        Group Cipher : TKIP
                        Pairwise Ciphers (2) : TKIP CCMP
                        Authentication Suites (1) : PSK
                    Quality=84/100  Signal level=43/100  
"""

NO_CHANNEL_OUTPUT = """Cell 06 - Address: 
                    ESSID:
                    Protocol:IEEE 802.11bgn
                    Mode:Master
                    Frequency:2.462 GHz (Channel 11)
                    Encryption key:on
                    Bit Rates:144 Mb/s
                    Extra:rsn_ie=30140100000fac040100000fac040100000fac020c00
                    IE: IEEE 802.11i/WPA2 Version 1
                        Group Cipher : CCMP
                        Pairwise Ciphers (1) : CCMP
                        Authentication Suites (1) : PSK
                    Quality=93/100  Signal level=10/100 
"""

LIST_INDEX_ERROR = """Cell 04 - Address: 50:06:04:C3:4D:93
                    Protocol:11g/n BW20
                    ESSID:""
                    Mode:Managed
                    Frequency:2.412 GHz (Channel 1)
                    Quality=94/100  Signal level=-53 dBm  Noise level=-92 dBm
                    Encryption key:off
                    Bit Rates:144 Mb/s
"""

FREQUENCY_NO_CHANNEL_OUTPUT = """Cell 01 - Address: 58:6D:8F:2B:DA:8E
                    Channel:149
                    Frequency:5.745 GHz
                    Quality=65/70 Signal level=-45 dBm
                    Encryption key:on
                    ESSID:"3408TT"
                    Bit Rates:6 Mb/s; 9 Mb/s; 12 Mb/s; 18 Mb/s; 24 Mb/s
                    36 Mb/s; 48 Mb/s; 54 Mb/s
                    Mode:Master
                    Extra:tsf=0000000edea58e3a
                    Extra: Last beacon: 140ms ago
                    IE: Unknown: 0006333430385454
                    IE: Unknown: 01088C129824B048606C
                    IE: IEEE 802.11i/WPA2 Version 1
                        Group Cipher : CCMP
                        Pairwise Ciphers (1) : CCMP
                        Authentication Suites (1) : PSK
                    IE: Unknown: 2D1AEE081AFFFF000001000000000000000000000000000000000000
                    IE: Unknown: 3D16950D0000000000000000000000000000000000000000
                    IE: Unknown: DD090010180200F02C0000
                    IE: Unknown: DD180050F2020101800003A4000027A4000042435E0062322F00
"""

ABSOLUTE_QUALITY = """Cell 04 - Address: 50:06:04:C3:4D:93
                    Protocol:11g/n BW20
                    ESSID:""
                    Mode:Managed
                    Frequency:2.412 GHz (Channel 1)
                    Quality:38 Signal level:16 Noise level:0
                    Encryption key:off
                    Bit Rates:144 Mb/s
"""

NO_SSID_AT_ALL = """Cell 10 - Address: 02:CA:FE:CA:CA:40
                    Channel:5
                    Frequency:2.432 GHz (Channel 5)
                    Quality=61/70  Signal level=-49 dBm  
                    Encryption key:on
                    Bit Rates:1 Mb/s; 2 Mb/s; 5.5 Mb/s; 11 Mb/s; 6 Mb/s
                              9 Mb/s; 12 Mb/s; 18 Mb/s
                    Bit Rates:24 Mb/s; 36 Mb/s; 48 Mb/s; 54 Mb/s
                    Mode:Ad-Hoc
                    Extra:tsf=000002744a259753
                    Extra: Last beacon: 76ms ago
                    IE: Unknown: 010882040B160C121824
                    IE: Unknown: 030105
                    IE: Unknown: 06020000
                    IE: Unknown: 32043048606C
                    IE: IEEE 802.11i/WPA2 Version 1
                        Group Cipher : CCMP
                        Pairwise Ciphers (1) : CCMP
                        Authentication Suites (1) : PSK
                    IE: Unknown: 2D1ACE111BFF00000000000000000000000100000000000000000000
                    IE: Unknown: 3D16050000000000FF000000000000000000000000000000
                    IE: Unknown: DD070050F202000100
"""
FREQUENCY_5G = """Cell 08 - Address: AC:22:05:25:3B:5B
                    Channel:100
                    Frequency:5.5 GHz (Channel 100)
                    Quality=50/70  Signal level=-60 dBm
                    Encryption key:on
                    ESSID:"TestWifi3827"
                    Bit Rates:6 Mb/s; 9 Mb/s; 12 Mb/s; 18 Mb/s; 24 Mb/s
                              36 Mb/s; 48 Mb/s; 54 Mb/s
                    Mode:Master
                    Extra:tsf=0000008a28a3e342
                    Extra: Last beacon: 3224ms ago
                    IE: IEEE 802.11i/WPA2 Version 1
                        Group Cipher : CCMP
                        Pairwise Ciphers (1) : CCMP
                        Authentication Suites (1) : PSK
"""
FREQUENCY_UNSUPPORTED = """Cell 08 - Address: AC:22:05:25:3B:5B
                    Channel:100
                    Frequency:3.6575 GHz (Channel 131)
                    Quality=50/70  Signal level=-60 dBm
                    Encryption key:on
                    ESSID:"TestWifi3827"
                    Bit Rates:6 Mb/s; 9 Mb/s; 12 Mb/s; 18 Mb/s; 24 Mb/s
                              36 Mb/s; 48 Mb/s; 54 Mb/s
                    Mode:Master
                    Extra:tsf=0000008a28a3e342
                    Extra: Last beacon: 3224ms ago
                    IE: Unknown: 000C5A6967676F43323835373132
                    IE: Unknown: 01088C129824B048606C
                    IE: Unknown: 030164
                    IE: Unknown: 200103
                    IE: IEEE 802.11i/WPA2 Version 1
                        Group Cipher : CCMP
                        Pairwise Ciphers (1) : CCMP
                        Authentication Suites (1) : PSK

"""
WSCFG_WPA1 = """network={
    ssid="WPA1"
    psk=a5e060ee3b1cb4b4f18b02b99a52d0ae037e90e428101eb8bae305580522e7be
    key_mgmt=WPA-PSK
    # bssid=None
}
"""
WSCFG_WPA2 = """network={
    ssid="WPA2"
    psk=2f14acebcf8e08d502f8d83d22a6addc92275f3e940c379a24f340c0705ebfee
    key_mgmt=WPA-PSK
    # bssid=None
}
"""
WSCFG_OPEN = """network={
    ssid="My Wireless Network"
    key_mgmt=NONE
}
"""
