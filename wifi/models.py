class Cell(object):
    def __init__(self):
        self.bitrates = []

    def __repr__(self):
        return 'Cell(ssid={ssid})'.format(**vars(self))
