#
# Copyright (C) 2020-2024 PyFPGA Project
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""
Implements support for an Open Source development flow.
"""

import os
import sys
from pathlib import Path

from pyfpga.project import Project

_RENAME = Path(__file__).parent / 'helpers' / 'rename_gowin_iopads.py'

_KNOWN_GOWIN_PARTS = {
    # Tang Nano 20K
    'GW2AR-LV18QN88C8/I7': {
        'family': 'gowin',
        'device': 'GW2AR-LV18QN88C8/I7',
        'gowin_family': 'GW2A-18C',
        'synth_family': 'gw2a',
    },
    'GW2A-LV18PG256C8/I7': {
        'family': 'gowin',
        'device': 'GW2A-LV18PG256C8/I7',
        'gowin_family': 'GW2A-18C',
        'synth_family': 'gw2a',
    },
    # Tang Primer 25K Dock
    'GW5A-LV25MG121NC1/I0': {
        'family': 'gowin',
        'device': 'GW5A-LV25MG121NC1/I0',
        'gowin_family': 'GW5A-25A',
        'synth_family': 'gw5a',
    },
    'GW5A-LV25MG121NES': {
        'family': 'gowin',
        'device': 'GW5A-LV25MG121NC1/I0',
        'gowin_family': 'GW5A-25A',
        'synth_family': 'gw5a',
    },
    # Tang Nano 9K
    'GW1NR-LV9QN88PC6/I5': {
        'family': 'gowin',
        'device': 'GW1NR-LV9QN88PC6/I5',
        'gowin_family': 'GW1N-9C',
        'synth_family': 'gw1n',
    },
    'GW1NR-LV9QN88C6/I5': {
        'family': 'gowin',
        'device': 'GW1NR-LV9QN88PC6/I5',
        'gowin_family': 'GW1N-9C',
        'synth_family': 'gw1n',
    },
}


class Openflow(Project):
    """Class to support Open Source tools."""

    def _configure(self):
        tool = 'openflow'
        self.conf['tool'] = tool
        self.conf['make_cmd'] = f'bash {tool}.sh'
        self.conf['make_ext'] = 'sh'
        self.conf['prog_bit'] = ['fs', 'svf', 'bit']
        self.conf['prog_cmd'] = f'bash {tool}-prog.sh'
        self.conf['prog_ext'] = 'sh'

    def add_mount(self, path):
        """Add a host directory bind-mount for Docker (in addition to auto-detected mounts).

        :param path: directory to mount at the same path inside the container
        :type path: str
        """
        self.logger.debug('Executing add_mount: %s', path)
        path = self._get_absolute(path, self.conf['make_ext'])
        if not Path(path).is_dir():
            raise NotADirectoryError(path)
        self.data.setdefault('extra_mounts', []).append(path)

    def _make_custom(self):
        info = get_info(self.data.get('part', 'hx8k-ct256'))
        self.data['family'] = info['family']
        self.data['device'] = info['device']
        if info['family'] == 'gowin':
            self.data['gowin_family'] = info['gowin_family']
            self.data['synth_family'] = info['synth_family']
            self.data['rename_iopads'] = _RENAME.resolve().as_posix()
            self.data['python'] = sys.executable
            self.data.setdefault('gowin_image', 'pyfpga/nextpnr-gowin:sid')
            # GW5A distributed RAM (RAM16SDP4) placement is incomplete; prefer BSRAM.
            if 'synth_extra' not in self.data:
                if info['synth_family'] == 'gw5a':
                    self.data['synth_extra'] = '-nolutram'
                env_extra = os.environ.get('GOWIN_YOSYS_SYNTH_EXTRA', '').strip()
                if env_extra:
                    self.data['synth_extra'] = env_extra
            freq = self.data.get('params', {}).get('FREQ')
            mhz = _freq_mhz(freq)
            if mhz is not None:
                self.data['nextpnr_freq'] = mhz
            self.data['cst_files'] = [
                path for path in self.data.get('constraints', {})
                if path.endswith('.cst')
            ]
        else:
            self.data['package'] = info['package']
        self.data['mounts'] = _collect_docker_mounts(self)

    def _prog_custom(self):
        info = get_info(self.data.get('part', 'hx8k-ct256'))
        self.data['family'] = info['family']
        self.data['mounts'] = _collect_docker_mounts(self)
        if info['family'] == 'gowin':
            self.data['gowin_board'] = self.data.get('gowin_board', 'tangnano')

    @staticmethod
    def _get_absolute(path, ext):
        return Path(path).resolve().as_posix()


def _collect_docker_mounts(prj):
    """Return host paths to bind-mount so resolved RTL paths are visible in Docker."""
    home = Path.home().resolve()
    extra = list(prj.data.get('extra_mounts', []))
    candidates = []
    for path in prj.data.get('files', {}):
        candidates.append(path)
    for path in prj.data.get('includes', []):
        candidates.append(path)
    for path in prj.data.get('constraints', {}):
        candidates.append(path)
    candidates.append(str(Path.cwd().resolve()))
    candidates.extend(extra)

    roots = set()
    for raw in candidates:
        path = Path(raw).resolve()
        if path.is_file():
            path = path.parent
        mount = _mount_root_outside_home(path, home)
        if mount is not None:
            roots.add(mount)

    ordered = sorted(roots, key=len)
    minimal = []
    for root in ordered:
        if any(root != other and root.startswith(other + os.sep) for other in minimal):
            continue
        minimal.append(root)
    return minimal


def _mount_root_outside_home(path, home):
    """Bind-mount root for *path* when it lives outside *home* (e.g. /mnt/sda)."""
    resolved = Path(path).resolve()
    if resolved.is_file():
        resolved = resolved.parent
    try:
        resolved.relative_to(home)
        return None
    except ValueError:
        pass
    parts = resolved.parts
    if len(parts) >= 3 and parts[0] == '/':
        # e.g. /mnt/sda/projects/... -> mount /mnt/sda
        return str(Path(parts[0]) / parts[1] / parts[2])
    if len(parts) >= 2 and parts[0] == '/':
        return str(Path(parts[0]) / parts[1])
    return None


def get_info(part):
    """Get info about the FPGA part.

    :param part: the FPGA part as specified by the tool
    :returns: a dict with the keys family, device and package (plus gowin fields)
    """
    key = str(part).strip()
    upper = key.upper().replace(' ', '')
    if upper.startswith(('GW1N', 'GW1NZ', 'GW1NS', 'GW2A', 'GW5A')):
        return _get_info_gowin(key)

    part = part.lower().replace(' ', '')
    # Looking for the family
    family = None
    families = [
        # From <YOSYS>/techlibs/xilinx/synth_xilinx.cc
        'xcup', 'xcu', 'xc7', 'xc6s', 'xc6v', 'xc5v', 'xc4v', 'xc3sda',
        'xc3sa', 'xc3se', 'xc3s', 'xc2vp', 'xc2v', 'xcve', 'xcv'
    ]
    for item in families:
        if part.startswith(item):
            family = item
            break
    families = [
        # From <nextpnr>/ice40/main.cc
        'lp384', 'lp1k', 'lp4k', 'lp8k', 'hx1k', 'hx4k', 'hx8k',
        'up3k', 'up5k', 'u1k', 'u2k', 'u4k'
    ]
    if part.startswith(tuple(families)):
        family = 'ice40'
    families = [
        # From <nextpnr>/ecp5/main.cc
        '12k', '25k', '45k', '85k', 'um-25k', 'um-45k', 'um-85k',
        'um5g-25k', 'um5g-45k', 'um5g-85k'
    ]
    if part.startswith(tuple(families)):
        family = 'ecp5'
    # Looking for the other values
    device = None
    package = None
    aux = part.split('-')
    if len(aux) == 2:
        device = aux[0]
        package = aux[1]
    elif len(aux) == 3:
        device = f'{aux[0]}-{aux[1]}'
        package = aux[2]
    else:
        valid = 'DEVICE-PACKAGE'
        raise ValueError(f'Invalid PART format ({valid})')
    if family in ['lp4k', 'hx4k']:  # See http://www.clifford.at/icestorm
        device = device.replace('4', '8')
        package += ":4k"
    if family == 'ecp5':
        package = package.upper()
    # Finish
    return {
        'family': family,
        'device': device,
        'package': package
    }


def _get_info_gowin(part):
    if not part or not str(part).strip():
        raise ValueError('Invalid PART format (Gowin part name)')
    if part in _KNOWN_GOWIN_PARTS:
        return dict(_KNOWN_GOWIN_PARTS[part])
    upper = str(part).upper().replace(' ', '')
    if upper.startswith('GW5A'):
        return {
            'family': 'gowin',
            'device': part,
            'gowin_family': 'GW5A-25A',
            'synth_family': 'gw5a',
        }
    if upper.startswith('GW2A'):
        return {
            'family': 'gowin',
            'device': part,
            'gowin_family': 'GW2A-18C',
            'synth_family': 'gw2a',
        }
    if upper.startswith('GW1N'):
        gowin_family = (
            'GW1N-9C' if ('9C' in upper or '9QN' in upper or '9C6' in upper)
            else 'GW1N-9'
        )
        return {
            'family': 'gowin',
            'device': part,
            'gowin_family': gowin_family,
            'synth_family': 'gw1n',
        }
    raise ValueError(
        f'Unsupported Gowin Openflow PART ({part}); try GW2AR-LV18QN88C8/I7, '
        'GW5A-LV25MG121NC1/I0, or GW1NR-LV9QN88PC6/I5'
    )


def _freq_mhz(freq):
    """Map a FREQ parameter in Hz (e.g. 27000000) to a nextpnr --freq value."""
    if freq is None:
        return None
    try:
        hertz = float(freq)
    except (TypeError, ValueError):
        return None
    if hertz >= 1000:
        mhz = hertz / 1e6
        return f'{mhz:g}'
    return None
