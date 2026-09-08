#
# Copyright (C) 2026 PyFPGA Project
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""
Implements support for the Gowin Yosys / nextpnr-himbaechel / gowin_pack flow.
"""

import sys
from pathlib import Path

from pyfpga.project import Project

_RENAME = Path(__file__).parent / 'helpers' / 'rename_gowin_iopads.py'

# nextpnr --device is the full part; --vopt family= is the Apicula chipdb.
_KNOWN_PARTS = {
    'GW2AR-LV18QN88C8/I7': {
        'device': 'GW2AR-LV18QN88C8/I7',
        'family': 'GW2A-18C',
        'synth_family': 'gw2a',
    },
}


class GowinYosys(Project):
    """Class to support Gowin OSS (yosys + nextpnr-himbaechel + gowin_pack)."""

    def _configure(self):
        tool = 'gowin_yosys'
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
        self.data['rename_iopads'] = _RENAME.resolve().as_posix()
        self.data['python'] = sys.executable
        freq = self.data.get('params', {}).get('FREQ')
        mhz = _freq_mhz(freq)
        if mhz is not None:
            self.data['nextpnr_freq'] = mhz
        self.data['cst_files'] = [
            path for path in self.data.get('constraints', {})
            if path.endswith('.cst')
        ]

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
    if upper.startswith('GW2A'):
        return {
            'device': key,
            'family': 'GW2A-18C',
            'synth_family': 'gw2a',
        }
    raise ValueError(
        f'Unsupported Gowin OSS PART ({part}); try GW2AR-LV18QN88C8/I7'
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
