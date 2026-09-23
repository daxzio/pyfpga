#
# Copyright (C) 2026 PyFPGA Project
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""
Implements support for the Gowin Yosys / nextpnr-himbaechel / gowin_pack flow.
"""

import os
from pathlib import Path

from pyfpga.project import Project

# nextpnr --device is the full part; --vopt family= is the Apicula chipdb name.
# Host nextpnr builds often ship only GW2A chipdb; set NEXTPNR_GOWIN_CHIPDB_DIR
# to a directory of chipdb-*.bin (e.g. extracted from pyfpga/nextpnr-gowin:sid).
_KNOWN_PARTS = {
    # Tang Nano 20K
    'GW2AR-LV18QN88C8/I7': {
        'device': 'GW2AR-LV18QN88C8/I7',
        'family': 'GW2A-18C',
        'synth_family': 'gw2a',
    },
    'GW2A-LV18PG256C8/I7': {
        'device': 'GW2A-LV18PG256C8/I7',
        'family': 'GW2A-18C',
        'synth_family': 'gw2a',
    },
    # Tang Primer 25K Dock (Gowin device DB / nextpnr use NC1/I0)
    'GW5A-LV25MG121NC1/I0': {
        'device': 'GW5A-LV25MG121NC1/I0',
        'family': 'GW5A-25A',
        'synth_family': 'gw5a',
    },
    'GW5A-LV25MG121NES': {
        'device': 'GW5A-LV25MG121NC1/I0',
        'family': 'GW5A-25A',
        'synth_family': 'gw5a',
    },
    # Tang Nano 9K
    'GW1NR-LV9QN88PC6/I5': {
        'device': 'GW1NR-LV9QN88PC6/I5',
        'family': 'GW1N-9C',
        'synth_family': 'gw1n',
    },
    'GW1NR-LV9QN88C6/I5': {
        'device': 'GW1NR-LV9QN88PC6/I5',
        'family': 'GW1N-9C',
        'synth_family': 'gw1n',
    },
}


class GowinRaw(Project):
    """Class to support Gowin OSS (yosys + nextpnr-himbaechel + gowin_pack)."""

    def _configure(self):
        tool = 'gowin_raw'
        self.conf['tool'] = tool
        self.conf['make_cmd'] = f'bash {tool}.sh'
        self.conf['make_ext'] = 'sh'
        self.conf['prog_bit'] = ['fs', 'bin']
        self.conf['prog_cmd'] = f'bash {tool}-prog.sh'
        self.conf['prog_ext'] = 'sh'

    def _make_custom(self):
        if 'part' not in self.data:
            self.data['part'] = 'GW2AR-LV18QN88C8/I7'
        info = get_info(self.data['part'])
        self.data['device'] = info['device']
        self.data['family'] = info['family']
        self.data['synth_family'] = info['synth_family']
        # GW5A distributed RAM (RAM16SDP4) placement is incomplete in current
        # nextpnr chipdbs; prefer BSRAM unless the caller overrides.
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
        chipdb = resolve_chipdb(self.data['family'], self.data.get('nextpnr_chipdb'))
        if chipdb:
            self.data['nextpnr_chipdb'] = chipdb

    def _prog_custom(self):
        info = get_info(self.data.get('part', 'GW2AR-LV18QN88C8/I7'))
        self.data['family'] = info['family']

    @staticmethod
    def _get_absolute(path, ext):
        return Path(path).resolve().as_posix()


def get_info(part):
    """Get nextpnr / synth_gowin names for a Gowin part.

    :param part: Gowin part, e.g. ``GW2AR-LV18QN88C8/I7``
    :returns: dict with device, family (chipdb), synth_family (yosys)
    """
    if not part or not str(part).strip():
        raise ValueError('Invalid PART format (Gowin part name)')
    key = str(part).strip()
    if key in _KNOWN_PARTS:
        return dict(_KNOWN_PARTS[key])
    upper = key.upper().replace(' ', '')
    if upper.startswith('GW5A'):
        return {
            'device': key,
            'family': 'GW5A-25A',
            'synth_family': 'gw5a',
        }
    if upper.startswith('GW2A'):
        return {
            'device': key,
            'family': 'GW2A-18C',
            'synth_family': 'gw2a',
        }
    if upper.startswith('GW1N'):
        # Tang Nano 9K and other GW1N-9 / GW1NR parts
        family = 'GW1N-9C' if ('9C' in upper or '9QN' in upper or '9C6' in upper) else 'GW1N-9'
        return {
            'device': key,
            'family': family,
            'synth_family': 'gw1n',
        }
    raise ValueError(
        'Unsupported Gowin OSS PART ({}); try GW2AR-LV18QN88C8/I7, '
        'GW5A-LV25MG121NC1/I0, or GW1NR-LV9QN88PC6/I5'.format(part)
    )


def resolve_chipdb(family: str, explicit=None) -> str | None:
    """Return an absolute chipdb path, or None to use nextpnr's default share.

    Resolution order:
    1. ``explicit`` / already-set path
    2. ``NEXTPNR_GOWIN_CHIPDB`` (file)
    3. ``NEXTPNR_GOWIN_CHIPDB_DIR`` / ``chipdb-{family}.bin`` if that file exists
    """
    if explicit:
        path = Path(explicit).expanduser()
        if path.is_file():
            return path.resolve().as_posix()
        raise FileNotFoundError(f'nextpnr chipdb not found: {path}')

    env_file = os.environ.get('NEXTPNR_GOWIN_CHIPDB', '').strip()
    if env_file:
        path = Path(env_file).expanduser()
        if not path.is_file():
            raise FileNotFoundError(f'NEXTPNR_GOWIN_CHIPDB not found: {path}')
        return path.resolve().as_posix()

    env_dir = os.environ.get('NEXTPNR_GOWIN_CHIPDB_DIR', '').strip()
    if env_dir:
        path = Path(env_dir).expanduser() / f'chipdb-{family}.bin'
        if path.is_file():
            return path.resolve().as_posix()
        # Dir set but this family missing — fall through to default share
    return None


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
