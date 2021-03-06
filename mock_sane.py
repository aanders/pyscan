import time

from mock_pil import Image

MOCK_NUM_DEVICES = 2

class _SaneIterator:
    """
    Iterator for ADF scans.
    """

    def __init__(self, device):
        self.device = device

    def __iter__(self):
        return self

    def __del__(self):
        self.device.cancel()

    def __next__(self):
        try:
            self.device.start()
            return self.device.snap(True)
        except Exception as e:
            raise StopIteration


class SaneDev:

    def __init__(self, devname):
        self.devname = devname
        self.mode = 'Color'
        self.page_height = 292
        self.resolution = 300
        self.contrast = 0
        self.source = 'ADF Front'
        self.page_loaded = 1
        self.scanner_model = ('Fujitsu', 'ScanSnap S300i')
        self._count = 0


    def __getitem__(self, name):
        if name == 'mode':
            return self.mode
        elif name == 'page_height':
            return self.page_height
        elif name == 'resolution':
            return self.resolution
        elif name == 'contrast':
            return self.contrast
        elif name == 'source':
            return self.source
        elif name == 'page_loaded':
            return self.page_loaded
        else:
            raise KeyError("No such option {}".format(name))

    def __setitem__(self, name, val):
        if name == 'mode':
            self.mode = val
        elif name == 'page_height':
            self.page_height = val
        elif name == 'resolution':
            self.resolution = val
        elif name == 'contrast':
            self.contrast = val
        elif name == 'source':
            self.source = val
        elif name == 'page_height':
            self.page_height = val
        else:
            raise KeyError("No such option {}".format(name))

    def start(self):
        pass

    def close(self):
        pass

    def cancel(self):
        pass

    def snap(self, no_cancel=False):
        time.sleep(2)
        self._count += 1
        if self._count > 5:
            raise StopIteration
        return Image.open('image{}'.format(self._count))

    def multi_scan(self):
        return _SaneIterator(self)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

def init():
    return 42, 0, 0

def get_devices():
    time.sleep(1)
    device_1 = ('epjitsu:libusb:001:004', 'Fujitsu', 'ScanSnap S1300i', 'scanner')
    device_2 = ('epson:libusb:001:005', 'Epson', 'DummyScanner', 'scanner')
    devices = []
    if MOCK_NUM_DEVICES >= 1:
        devices.append(device_1)
    if MOCK_NUM_DEVICES >= 2:
        devices.append(device_2)
    return devices

def open(devname):
    return SaneDev(devname)

def exit():
    pass
