import netifaces

from .scheme import Scheme


def get_ip_address_for_interface(interface):
    ip_addresses = netifaces.ifaddresses(interface)
    ipv4_list = ip_addresses.get(netifaces.AF_INET)
    try:
        ipv4 = ipv4_list[0]['addr']
    except (IndexError, KeyError, TypeError):
        ipv4 = None
    ipv6_list = ip_addresses.get(netifaces.AF_INET6)
    try:
        ipv6 = ipv6_list[0]['addr']
    except (IndexError, KeyError, TypeError):
        ipv6 = None

    return ipv4, ipv6


class Connection(object):
    """
    The connection object returned when connecting to a Scheme.
    """
    def __init__(self, scheme, ipv4=None, ipv6=None):
        self.scheme = scheme
        self.ipv4 = ipv4
        self.ipv6 = ipv6

    def __repr__(self):
        return 'Connection(scheme={scheme!r}, ipv4={ipv4}, ipv6={ipv6})'.format(**vars(self))

    @classmethod
    def current_for_scheme(cls, scheme):
        """
        Returns a connection object based on the current connection for the
        specified scheme.  If it is determined that there is no connection,
        this may return None.
        """
        ipv4, ipv6 = get_ip_address_for_interface(scheme.interface)

        if not ipv4 and not ipv6:
            return None

        return cls(scheme, ipv4=ipv4, ipv6=ipv6)

    @classmethod
    def current(cls, interface):
        """
        Derives the current connection based on the current scheme for the
        specified interface.
        """
        schemes = Scheme.current(interface)
        if schemes is None:
            return None
        elif not schemes:
            scheme = Scheme(interface, None)
        else:
            scheme = schemes[0]

        return cls.current_for_scheme(scheme)
