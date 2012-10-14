from wifi.keyderiv import *

# These test cases were generated using a Linksys WRT160. Hopefully other
# devices use the same algorithms.

def test_64():
    assert wep_64('foobar') == 'a4beb3b8ec'
    assert wep_64('z') == 'b5715b3121'
    assert wep_64('zazazax') == '2039c027b1'
    assert wep_64('lorem ipsum') == 'a04599bf1b'
    assert wep_64('Lorem Ipsum') == '9798f4b529'


def test_128():
    assert wep_128('foobar') == '49d68437b1ffb0db3fdf2d4a93'
    assert wep_128('foobara') == '48d5dcff3b82ce7dc18961b0b2'
    assert wep_128('x') == 'c1bb4f81d892b2d57947682aeb'
    assert wep_128('xa') == '26ac564e2b268e107abbbc8c36'
    assert wep_128('xaf') == '19467282900981a3e213da186b'
    assert wep_128('aaaaaaaaaaaaaaaa') == '014842d480b571495a4a036379'


def test_wpa():
    assert wpa2('asdfasdfasdf', 'asdf') == '9bbab1b4fc33b10e51b71f2b4c0a208694834c22beea2d2c2fc496e47ee7d8ba'
    assert wpa2('alfalfa sprouts', 'foobar') == '2dcdc9e701707fdb4c5a9c22966637172fa314a5399fbb7c9a7786bd266e0aaf'
