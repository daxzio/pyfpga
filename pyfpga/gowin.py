#
# Copyright (C) 2019-2024 PyFPGA Project
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""
Implements support for Gowin.
"""

from pathlib import Path
from pyfpga.project import Project


class Gowin(Project):
    """Class to support Gowin projects."""

    def _configure(self):
        tool = 'gowin'
        command = 'gw_sh'
        self.conf['tool'] = tool
        self.conf['make_cmd'] = f'{command} {tool}.tcl'
        self.conf['make_ext'] = 'tcl'
        self.conf['prog_bit'] = ['fs', 'bin']
        self.conf['prog_cmd'] = f'{command} {tool}-prog.tcl'
        self.conf['prog_ext'] = 'tcl'

    def _make_custom(self):
        if 'part' not in self.data:
            self.data['part'] = 'GW2AR-LV18QN88C8/I7'

    def add_param(self, name, value):
        """Add a Parameter/Generic Value.

        :param name: parameter/generic name
        :type name: str
        :param value: parameter/generic value
        :type name: str
        """
        self.logger.debug('Executing add_param: %s : %s', name, value)
        self.data.setdefault('params', {})[name] = value
        raise NotImplementedError("Gowin has not implemented Params yet")
        
    def add_define(self, name, value):
        """Add a Verilog Defile Value.

        :param name: define name
        :type name: str
        :param value: define value
        :type name: str
        """
        self.logger.debug('Executing add_define: %s : %s', name, value)
        self.data.setdefault('defines', {})[name] = value
        raise NotImplementedError("Gowin has not implemented defines yet")

    def _get_bitstream(self, bitstream=None):
        if not bitstream:
            for ext in self.conf['prog_bit']:
                candidate = Path(self.odir) / f'{self.data["project"]}/impl/pnr/{self.data["project"]}.{ext}'
                print(candidate)
                if candidate.is_file():
                    bitstream = candidate
                    break
        if not bitstream or not Path(bitstream).is_file():
            raise FileNotFoundError(bitstream)
        return self._get_absolute(bitstream, self.conf['prog_ext'])
