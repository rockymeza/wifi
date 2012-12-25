import subprocess
import re
import textwrap

from wifi.pbkdf2 import pbkdf2_hex
from wifi.utils import match
from wifi.scan import scan


scheme_re = re.compile(r'(?:iface|map)\s+wlan0-(\w+)')


def configure(scheme, cell):
    """
    Returns an iface configuration suitable for
    /etc/network/interfaces.  If the cell is encrypted, will ask for
    password.
    """
    context = {
        'scheme': scheme,
        'cell': cell,
    }

    if not cell.encrypted:
        template = """
        iface wlan0-{scheme} inet dhcp
            wireless-essid {cell.ssid}
            wireless-channel auto
        """
    else:
        if cell.encryption_type == 'wpa2':
            passkey = raw_input('wpa passkey> ')

            if len(passkey) != 64:
                passkey = pbkdf2_hex(passkey, cell.ssid, 4096, 32)

            template = """
            iface wlan0-{scheme} inet dhcp
                wpa-ssid {cell.ssid}
                wpa-psk  {passkey}
                wireless-channel auto
            """

            context.update({'passkey': passkey})

    return textwrap.dedent(template).format(**context)


def show(scheme, ssid=None):
    """
    Creates configuration for a scheme.
    """
    cells = scan()
    needle = ssid or scheme
    match_partial = lambda cell: match(needle, cell.ssid)

    matches = filter(match_partial, cells)

    num_matches = len(set(cell.ssid for cell in matches))

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
    with open('/etc/network/interfaces', 'r') as f:
        interfaces = f.read()

    return scheme_re.findall(interfaces)


def connect(scheme):
    assert scheme in get_schemes(), "I don't recognize that scheme"

    subprocess.check_call(['/sbin/ifdown', 'wlan0'])
    subprocess.check_call(['/sbin/ifup', 'wlan0=wlan0-{}'.format(scheme)])
