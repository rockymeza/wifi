from __future__ import division

import re
import textwrap

import wifi.subprocess_compat as subprocess
from wifi.exceptions import InterfaceError
from wifi.utils import db2dbm, pass2psk, logger, PrivilegedCommand


class Cell(object):
    """
    Presents a Python interface to the output of iwlist.
    """

    def __init__(self):
        self.ssid = None
        self.bitrates = []
        self.address = None
        self.channel = None
        self.encrypted = False
        self.encryption_type = None
        self.group_cipher = None
        self.pairwise_ciphers = []
        self.authentication_suites = []
        self.frequency = None
        self.frequency_norm = None
        self.mode = None
        self.quality = None
        self.signal = None
        self.noise = None

    def __repr__(self):
        return 'Cell(ssid={ssid})'.format(ssid=self.ssid)

    @classmethod
    def all(cls, interface, timeout=None, use_sudo=False):
        """
        Returns a list of all cells extracted from the output of iwlist.

        The timeout parameter (new in 0.8.0) is passed on to the subprocess
        module. If a postive number is given it is interpreted as the maximum
        number of seconds to wait for the command to complete. Fractions are
        supported.
        If the parameter is `None` (the default), then it blocks and waits
        indefinitely for the command to complete. This default will likely
        change to an acceptable timeout.

        The use_sudo parameter (new in 0.8.0) adds support for running the
        command as root, via the program `sudo(8)`. For now the default is
        False for backwards compatibility, but will change in 0.9.0 to true.

        :param interface: Interface name as shown by `ip a`
        :type interface: str
        :param timeout: Maximum number of seconds to wait for output.
        Default: None.
        :type timeout: float, int, None
        :param use_sudo: Whether or not to use sudo to run the command as root
        :type use_sudo: bool

        :raises InterfaceError: if running the command fails.
        :raises subprocess.TimeoutExpired: if the command timed out.
        """
        logger.debug('Scanning all on interface {}'.format(interface))
        command = PrivilegedCommand(
            '/sbin/iwlist', interface, 'scan', timeout=timeout,
            use_sudo=use_sudo
        )
        try:
            iwlist_scan = command(with_stderr=True)
        except subprocess.CalledProcessError as e:
            raise InterfaceError(e.output.strip())

        iwlist_scan = iwlist_scan.decode('utf-8')
        cells = map(Cell.from_string, cells_re.split(iwlist_scan)[1:])
        logger.debug('Scan succesful')

        return cells

    @classmethod
    def from_string(cls, cell_string):
        """
        Parses provided string and returns a Cell object for it.

        :param cell_string: Output of `iwlist` for one cell.
        """
        return normalize(cell_string)

    @classmethod
    def where(cls, interface, fn):
        """
        Runs a filter over the output of :meth:`all` and the returns
        a list of cells that match that filter.

        :param interface: Interface name as shown by `ip a`
        :type interface: str
        :param fn: Callback for the built-in `filter` method
        :type fn: callable
        """
        return list(filter(fn, cls.all(interface)))

    @property
    def bssid(self):
        return self.address

    @bssid.setter
    def bssid(self, value):
        self.address = value

    def gen_wpasup_cfg(self, passphrase=None, psk=None, file=None,
                       include_bssid=False):
        """
        Generate a wpa_supplicant(1) configuration for the cell

        Generates a configuration bit from the parsed cell that is equivalent to
        a `wpa_supplicant` network definition. A passphrase or psk must be
        provided if the cell is encrypted. If both are provided,
        no verification is done if they match and the psk is used. The actual
        passphrase is not returned in the output.

        The cell must have an ssid.

        :param passphrase: If provided, the raw passphrase for the cell's key
        :param psk: If provided, a hexencoded Pre Shared Key for the cell
        :param file: If provided, write to the file-like object.
        :param include_bssid: Whether to include the bssid.
        :type include_bssid: bool
        :return: The generated configuration
        """
        logger.debug(
            'Generating wpa_supplicant configuration for ssid %s', self.ssid
        )
        if self.ssid is None:
            raise ValueError('ssid required for wpa_supplicant configuration')
        retval = ''
        show_bssid = 'bssid' if include_bssid else '# bssid'
        if self.encrypted:
            if not passphrase and not psk:
                raise ValueError('A passphrase or Pre Shared Key is required '
                                 'for encrypted cells.')
            if 'wpa' in self.encryption_type:
                if 'PSK' in self.authentication_suites:
                    if not psk:
                        psk = pass2psk(self.ssid, passphrase)
                    retval = wpasup_psk_cfg_fmt.format(
                        ssid=self.ssid, psk=psk, show_bssid=show_bssid,
                        bssid=self.bssid
                    )
        else:
            retval = wpasup_open_cfg_fmt.format(ssid=self.ssid)

        if not retval:
            raise NotImplementedError('No support for this cell implemented')
        if file:
            file.write(retval)

        logger.debug('Generated config bit:\n%s', retval)
        return retval

cells_re = re.compile(r'Cell \d+ - ')

quality_re_dict = {
    'dBm': re.compile(
        r'Quality[=:](?P<quality>\d+/\d+).*Signal level[=:](?P<siglevel>-\d+) '
        'dBm?(.*Noise level[=:](?P<noiselevel>-\d+) dBm)?'
    ),
    'relative': re.compile(
        r'Quality[=:](?P<quality>\d+/\d+)\s.*Signal level[=:]'
        '(?P<siglevel>\d+/\d+)'
    ),
    'absolute': re.compile(
        r'Quality[=:](?P<quality>\d+)\s.*Signal level[=:](?P<siglevel>\d+)'
    )
}
frequency_re = re.compile(
    r'^(?P<frequency>[\d\.]+ .Hz)(?:[\s\(]+Channel\s+(?P<channel>\d+)[\s\)]+)?$'
)

LOWBOUND_FREQ_24 = 2.412
UPPERBOUND_FREQ_24 = 2.484

LOWBOUND_FREQ_5 = 4.915
UPPERBOUND_FREQ_5 = 5.865

key_translations = {
    'encryption key': 'encrypted',
    'essid': 'ssid',
}

wpasup_psk_cfg_fmt = """network={{
    ssid="{ssid:s}"
    psk={psk:s}
    key_mgmt=WPA-PSK
    {show_bssid:s}={bssid}
}}
"""

wpasup_open_cfg_fmt = """network={{
    ssid="{ssid:s}"
    key_mgmt=NONE
}}
"""


def identity(x):
    return x


def normalize_key(key):
    key = key.strip().lower()

    key = key_translations.get(key, key)

    return key.replace(' ', '')

normalize_value = {
    'ssid': lambda v: v.strip('"'),
    'encrypted': lambda v: v == 'on',
    'address': identity,
    'mode': identity,
    'channel': int,
}


def split_on_colon(string):
    key, _, value = map(lambda s: s.strip(), string.partition(':'))

    return key, value


def normalize(cell_block):
    # The cell blocks come in with every line except the first indented at
    # least 20 spaces.  This removes the first 20 spaces off of those lines.
    lines = textwrap.dedent(' ' * 20 + cell_block).splitlines()

    cell = Cell()
    logger.debug('Starting cell block with %d lines', len(lines))

    for line in lines:
        if line.startswith('Quality'):
            logger.debug('- Quality line')
            for re_name, quality_re in quality_re_dict.items():
                match_result = quality_re.search(line)
                if match_result is not None:
                    groups = match_result.groupdict()
                    cell.quality = groups['quality']
                    signal = groups['siglevel']
                    noise = groups.get('noiselevel')
                    if re_name == 'relative':
                        actual, total = map(int, signal.split('/'))
                        cell.signal = db2dbm(int((actual / total) * 100))
                    elif re_name == 'absolute':
                        cell.quality += '/100'
                        cell.signal = db2dbm(int(signal))
                    else:
                        cell.signal = int(signal)
                    if noise is not None:
                        cell.noise = int(noise)
                    break

        elif line.startswith('Bit Rates'):
            logger.debug('- Bit rates line')
            values = split_on_colon(line)[1].split('; ')

            # consume next line of bit rates, because they are split on
            # different lines, sometimes...
            if lines:
                while lines[0].startswith(' ' * 10):
                    values += lines.pop(0).strip().split('; ')

            cell.bitrates.extend(values)

        elif line.startswith('    Group Cipher'):
            logger.debug('- Group Cipher line')
            __, cell.group_cipher = split_on_colon(line)

        elif line.startswith('    Pairwise Ciphers'):
            logger.debug('- Pairwise ciphers line')
            key, value = split_on_colon(line)
            cell.pairwise_ciphers = value.split(' ')

        elif line.startswith('    Authentication Suites'):
            logger.debug('- Authentication suites line')
            key, value = split_on_colon(line)  # type: str, str
            if '802.1x' in value and cell.encryption_type == 'wpa2':
                cell.encryption_type = 'wpa2-enterprise'
            elif '802.1x' in value and cell.encryption_type == 'wpa':
                cell.encryption_type = 'wpa-enterprise'
            cell.authentication_suites = value.split(' ')

        elif ':' in line:
            logger.debug('- Line with colon')
            key, value = split_on_colon(line)
            key = normalize_key(key)

            if key == 'ie':
                if 'Unknown' in value:
                    continue

                # consume remaining block
                values = [value]
                while lines and lines[0].startswith(' ' * 4):
                    values.append(lines.pop(0).strip())

                if 'WPA2' in value and cell.encryption_type is None:
                    cell.encryption_type = 'wpa2'
                elif 'WPA' in value and cell.encryption_type is None:
                    cell.encryption_type = 'wpa'
                elif 'WPA' in value and cell.encryption_type == 'wpa2' or \
                        'WPA2' in value and cell.encryption_type == 'wpa':
                    cell.encryption_type = 'wpa/wpa2'
                
            if key == 'frequency':
                matches = frequency_re.search(value)
                cell.frequency = matches.group('frequency')
                f, __ = cell.frequency.split(' ', 1)
                f = float(f)
                if LOWBOUND_FREQ_24 <= f <= UPPERBOUND_FREQ_24:
                    cell.frequency_norm = '2.4Ghz'
                elif LOWBOUND_FREQ_5 <= f <= UPPERBOUND_FREQ_5:
                    cell.frequency_norm = '5Ghz'
                if matches.group('channel'):
                    cell.channel = int(matches.group('channel'))
            elif key in normalize_value:
                setattr(cell, key, normalize_value[key](value))
        else:
            logger.debug('- Line of no interest: "%s"', line.strip())

    # It seems that encryption types other than WEP need to specify their
    # existence.
    if cell.encrypted and not cell.encryption_type:
        logger.debug('Defaulting to WEP')
        cell.encryption_type = 'wep'

    return cell
