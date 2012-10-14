import subprocess
import re
import textwrap
import itertools

from wifi import keyderiv

scheme_re = re.compile(r'(?:iface|map)\s+wlan0-(\w+)')
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


def configuration(cell):
    """
    Returns a dictionary of configuration options for cell

    Asks for a password if necessary
    """
    if cell['encrypted'] == 'off':
        return {
            'wireless-essid': cell['ssid'],
            'wireless-channel': 'auto',
        }
    else:
        if cell.get('encryption_type') == 'WPA2':
            passkey = raw_input('wpa passkey> ')

            if len(passkey) != 64:
                passkey = keyderiv.wpa2(passkey, cell['ssid'])

            return {
                'wpa-ssid': cell['ssid'],
                'wpa-psk': passkey,
                'wireless-channel': 'auto',
            }
        # no encryption_type means WEP
        elif 'encryption_type' not in cell:
            key = raw_input('wep key> ')
            return {
                'wireless-essid': cell['ssid'],
                'wireless-key': key,
                'wireless-channel': 'auto',
            }
        else:
            raise NotImplementedError


def configure(scheme, cell):
    """
    Returns an iface configuration suitable for
    /etc/network/interfaces.  If the cell is encrypted, will ask for
    password.
    """

    config = configuration(cell)
    iface = "iface wlan0-{scheme} inet dhcp\n".format(scheme=scheme)
    options = '\n'.join("    {k} {v}".format(k=k, v=v) for k, v in config.items())
    return iface + options


def find_cell(query):
    cells = iwlist()
    match_partial = lambda cell: match(query, cell['ssid'])

    matches = filter(match_partial, cells)

    num_matches = len(set(cell['ssid'] for cell in matches))
    assert num_matches > 0, "Couldn't find a network that matches '{}'".format(query)
    assert num_matches < 2, "Found more than one network that matches '{}'".format(query)

    return matches[0]


def show(scheme, ssid=None):
    """
    Creates configuration for a scheme.
    """
    cell = find_cell(ssid or scheme)
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
    with open('/etc/network/interfaces', 'r') as f:
        interfaces = f.read()

    return scheme_re.findall(interfaces)


def connect(scheme, adhoc=False):
    if adhoc:
        cell = find_cell(scheme)
        config = configuration(cell)
        args = list(itertools.chain.from_iterable(
            ('-o', '{k}={v}'.format(k=k, v=v)) for k, v in config.items()))
        subprocess.check_call(['/sbin/ifdown', 'wlan0'])
        subprocess.check_call(['/sbin/ifup', 'wlan0'] + args)
    else:
        assert scheme in get_schemes(), "I don't recognize that scheme"

        subprocess.check_call(['/sbin/ifdown', 'wlan0'])
        subprocess.check_call(['/sbin/ifup', 'wlan0=wlan0-{}'.format(scheme)])
