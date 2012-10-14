from wifi.pbkdf2 import pbkdf2_hex
import hashlib

# Sources:
# http://svn.dd-wrt.com:8000/browser/src/router/httpd/validate/wepkey.c?rev=11516
# http://svn.openmoko.org/developers/werner/wep/wepkey.c
# http://stackoverflow.com/questions/2890438/how-can-i-generate-40-64-bit-wep-key-in-python
# http://mirror.umd.edu/roswiki/doc/unstable/api/wpa_supplicant/html/wpa__passphrase_8c_source.html


def wep_128(s):
    """
    Given a passphrase s, generate the wep-128 key for it.

    The first 26 characters of the hexdigest of the md5 of the first 64
    characters of s concatenated with itself over and over.
    """
    r = ""
    while len(r) < 64:
        r += s
    return hashlib.md5(r[:64]).hexdigest()[:26]


def wep_64(s, n=0):
    """
    Given a passphase s and zero-index key number n, generate the wep-64 key for it.
    """
    prn = 0
    for index, c in enumerate(s):
        prn ^= ord(c) << (8*(index & 3))
    keys = []
    def permute(prn):
        prn *= 0x343fd
        prn += 0x269ec3
        prn &= 0xFFFFFFFF
        return prn
    for i in range(n * 5):
        prn = permute(prn)
    out = ""
    for i in range(5):
        prn = permute(prn)
        out += "%02x" % ((prn >> 16) & 0xFF)
    return out


def wpa2(s, ssid):
    """
    WPA2 psk calculation.

    """
    return pbkdf2_hex(s, ssid, 4096, 32)
