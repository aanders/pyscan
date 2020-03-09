import argparse
import os
import sys

import mock_sane as sane

from dialog import Dialog

import toml

sane.MOCK_NUM_DEVICES = 1

class PyScanUi:

    VERSION = "0.1.0"
    APP_NAME = "pyscan"

    def __init__(self, args):
        self.device = None
        self.d = Dialog()
        self.d.set_background_title(self.banner())
        self.configs = args.config.get('configs')
        self.config = next(iter(self.configs)) if self.configs else dict()
        self.directory = ""
        self.filename = "FOO"

    def banner(self):
        banner_str = ' '.join((PyScanUi.APP_NAME, PyScanUi.VERSION))
        if self.device:
            banner_str += ' [{}]'.format(' '.join(self.device.scanner_model))
        return banner_str

    def start(self):
        dev_name = self.select_scanner()
        if dev_name:
            with sane.open(dev_name) as self.device:
                # Update background title to contain scanner name
                self.d.set_background_title(self.banner())
                self.main_loop()

    def select_scanner(self):
        sane_version = sane.init()
        self.d.infobox("\nPlease wait, detecting scanners...", title="SANE Version {}.{}.{}".format(*sane_version))
        devs = sane.get_devices()
        if len(devs) == 0:
            self.d.msgbox("No scanners found!")
            return None
        elif len(devs) == 1:
            return devs[0][0]
        else:
            # 0 => SANE descriptor (e.g. "epjitsu:libusb:001:004")
            # 1 => Vendor (e.g. "Fujitsu")
            # 2 => Model (e.g. "ScanSnap S1300i")
            model_name = lambda d: ' '.join((d[1], d[2]))
            # Mark the first device selected by default
            choices = ((d[0], model_name(d), d[0] == devs[0][0]) for d in devs)
            code, name = self.d.radiolist("Select a scanner to use",
                    choices=choices, height=10, width=72)
            return name if code == Dialog.OK else None

    def change_config(self):
        code, name = self.d.menu("Choose a configuration to load.\n\n"
                "Arrow keys to move, <Space> or <Enter> to select.",
                title="Select Configuration",
                choices=((config.get("_name"), config.get("_description"))
                    for config in self.configs),
                menu_height=5, height=15, width=72)
        if code == Dialog.OK:
            self.config = next(c for c in self.configs if c["_name"] == name)

    def change_directory(self):
        code, path = self.d.dselect(self.directory, title='Choose an output directory', height=30, width=90)
        if code == Dialog.OK:
            self.directory = path

    def setup_menu(self):
        has_config = self.configs is not None
        choices = []
        if has_config:
            choices.append(('Config', 'Select scanning configuration'))
        choices.append(('Directory', 'Select output directory'))
        code, tag = self.d.menu("Setup Menu", choices=choices)
        if code == Dialog.OK:
            if tag == 'Config':
                self.change_config()
            elif tag == 'Directory':
                self.change_directory()

    def config_to_text(self, width=80, indent=0):
        output = "Output directory: {}".format(self.directory)
        title = "Config: {}".format(self.config.get("_name", "<none>"))
        lines = [output, title, '', self.config.get("_description", '')]
        for k, v in self.config.items():
            if k[0] == '_':
                continue
            pad = width - indent - len(k) - len(str(v))
            NBSP = '\u00a0'
            lines.append(''.join((NBSP*indent, k.title(), '.'*pad, str(v))))
        return '\n'.join(lines)

    def main_menu(self):
        text = self.config_to_text(width=42, indent=4)
        code = self.d.yesno(text,
                title="Main Menu", extra_button=True, height=15, width=50,
                ok_label="Scan", extra_label="Setup", cancel_label="Quit")
        return code

    def do_scan(self):
        filename = "Scan_{}.pdf".format(
                datetime.datetime.now().strftime("%Y%m%d%H%M%S"))

        if config is not None:
            for k, v in config.items():
                self.device[k] = v
        with tempfile.TemporaryDirectory() as tmpdir:
            i = 0
            for img in self.device.multi_scan():
                img.save(os.path.join(tmpdir, "out{}.pnm".format(i)))
                i += 1
            # Collect the output files and combine into a single PDF
            files = sorted(glob.iglob(os.path.join(tmpdir, "*.pnm")))
            if config and config.get("rotate_first"):
                from PIL import Image # Only require this if actually needed
                with Image.open(files[0]) as i:
                    i.transpose(Image.ROTATE_180).save(files[0],
                                                       format=i.format)
            subprocess.run(('convert', '-density', '300', *files,
                            os.path.join(self.directory, filename)), check=True)

    def main_loop(self):
        while True:
            code = self.main_menu()
            if code == Dialog.OK:
                self.do_scan()
            elif code == Dialog.EXTRA:
                self.setup_menu()
            else:
                break


class PyScanConfig:

    DEFAULT_NAME = 'pyscan.toml'

    @classmethod
    def parse_config(cls, raw_config):
        # Set environment variables
        for k in raw_config.get('env', dict()).keys():
            raw_config['env'][k] = os.path.expandvars(raw_config['env'][k])
            os.environ[k] = raw_config['env'][k]
        return raw_config

    @classmethod
    def load_config(cls, path=None, name=None):
        if path is None:
            path = (os.path.expanduser('~/.config'), '/etc')
        if name is None:
            name = PyScanConfig.DEFAULT_NAME
        config = None
        for p in path:
            try:
                with open(os.path.join(p, name)) as f:
                    config = PyScanConfig.parse_config(toml.load(f))
                # Successfully loaded config
                break
            except FileNotFoundError as e:
                pass
        return config


    @classmethod
    def load_from_file(cls, filename):
        path = os.path.dirname(os.path.abspath(filename))
        name = os.path.basename(filename)
        config = PaperlessUtilsConfig.load_config(path=(path,), name=name)
        if config is None:
            raise FileNotFoundError(filename)
        return config


class PyScanArgs:

    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('--config', '-c', dest='conffile',
                help="Use an alternate config file")

    def parse(self, argv):
        return self.parser.parse_args(args=argv)


def main(argv=None):
    args = PyScanArgs().parse(argv)
    if args.conffile:
        args.config = PyScanConfig.load_from_file(args.conffile)
    else:
        args.config = PyScanConfig.load_config() or dict()

    try:
        PyScanUi(args).start()
    except Exception as e:
        # Clear screen before raising exception
        os.system("clear")
        raise
    else:
        os.system("clear")
    finally:
        sane.exit()

if __name__ == '__main__':
    sys.exit(main())
