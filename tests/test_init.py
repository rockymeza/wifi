from unittest import TestCase

from wifi.scan import Cell


class CorrectInitTest(TestCase):
    fields = {"ssid": None,
              "bitrates": [],
              "address": None,
              "channel": None,
              "encrypted": False,
              "encryption_type": None,
              "frequency": None,
              "mode": None,
              "quality": None,
              "signal": None}

    def test_empty_init(self):
        tcell = Cell()

        for field, value in self.fields.items():
            self.assertEqual(value, getattr(tcell, field))
