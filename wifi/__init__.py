import subprocess
import re
import textwrap
import os
import sys

from wifi.pbkdf2 import pbkdf2_hex


cells_re = re.compile(r'Cell \d+ - Address:')

extractors = {
    'ssid': re.compile(r'SSID:"([^"]*)"'),
    'signal': re.compile(r'Signal level=(-\d+) dBm'),
    'encrypted': re.compile(r'Encryption key:(on|off)'),
    'encryption_type': re.compile(r'IEEE 802.11./(WPA2)'),
}


def iwlist():
    """
    Returns a dictionary of available cells.  The dictionaries will
    contain ``ssid``, ``signal``, and ``encrypted`` and may contain
    ``encryption_type``.
    """
    scan = subprocess.check_output(['/sbin/iwlist', 'wlan0', 'scan'])

    cell_blocks = cells_re.split(scan)

    cells = []

    for block in cell_blocks:
        cell = {}

        for key, regex in extractors.iteritems():
            match = regex.search(block)

            if match:
                cell[key] = match.group(1)

        if cell:
            cells.append(cell)

    return cells


def match(needle, haystack):
    """
    Command-T-style string matching.
    """
    score = 1
    j = 0
    last_match = 0
    needle = needle.lower()
    haystack = haystack.lower()

    for c in needle:
        while j < len(haystack) and haystack[j] != c:
            j += 1
        if j >= len(haystack):
            return 0
        score += 1 / (last_match + 1.)
        last_match = j
        j += 1
    return score


def print_table(matrix):
    """
    Prints a left-aligned table of elements.
    """
    lengths = [max(map(len, column)) for column in zip(*matrix)]
    format = '  '.join('{{:<{0}}}'.format(length) for length in lengths)

    for row in matrix:
        print(format.format(*row))


def configure(scheme, cell):
    """
    Returns an iface configuration suitable for
    /etc/network/interfaces.  If the cell is encrypted, will ask for
    password.
    """
    context = {
        'scheme': scheme,
    }
    context.update(cell)

    if cell['encrypted'] == 'off':
        template = """
        iface wlan0-{scheme} inet dhcp
            wireless-essid {ssid}
            wireless-channel auto
        """
    else:
        if cell.get('encryption_type') == 'WPA2':
            passkey = raw_input('wpa passkey> ')

            if len(passkey) != 64:
                passkey = pbkdf2_hex(passkey, cell['ssid'], 4096, 32)

            template = """
            iface wlan0-{scheme} inet dhcp
                wpa-ssid {ssid}
                wpa-psk  {passkey}
                wireless-channel auto
            """

            context.update({'passkey': passkey})

    return textwrap.dedent(template).format(**context)


def show(scheme, ssid=None):
    """
    Creates configuration for a scheme.
    """
    cells = iwlist()
    needle = ssid or scheme
    match_partial = lambda cell: match(needle, cell['ssid'])

    matches = filter(match_partial, cells)

    num_matches = len(set(cell['ssid'] for cell in matches))

    assert num_matches > 0, "Couldn't find a network that matches '{}'".format(needle)
    assert num_matches < 2, "Found more than one network that matches '{}'".format(needle)

    cell = matches[0]

    return configure(scheme, cell)


def add(scheme, ssid=None):
    """
    Creates configuration for a scheme and saves it to
    /etc/network/interfaces.
    """
    assert scheme not in get_schemes(), "That scheme has already been used"

    configuration = show(scheme, ssid)

    with open('/etc/network/interfaces', 'a') as f:
        f.write(configuration)


def get_schemes():
    """
    Returns a list of schemes that have already been configured.
    """
    return subprocess.check_output(['/sbin/ifscheme', '-l']).strip().split('\n')


def connect(scheme):
    assert scheme in get_schemes(), "I don't recognize that scheme"

    subprocess.check_call(['/sbin/ifdown', 'wlan0'])
    subprocess.check_call(['/sbin/ifscheme', scheme])
    subprocess.check_call(['/sbin/ifup', 'wlan0'])


def init():
    """
    Ensures that ifscheme is installed and configured.
    """
    if not os.path.exists('/sbin/ifscheme'):
        sys.exit(sys.argv[0] + " requires ifscheme, please install it.")

    with open('/etc/network/interfaces', 'a+') as f:
        assert 'mapping wlan0' not in f.read(), "/etc/network/interfaces already seems to be configured."

        f.write(textwrap.dedent("""
        mapping wlan0
            script ifscheme-mapping
        """))
