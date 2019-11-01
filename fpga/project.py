#
# Copyright (C) 2019 INTI
# Copyright (C) 2019 Rodrigo A. Melo
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

"""fpga.project

Main Class of PyFPGA, which provides functionalities to create a project,
generate files and transfer to a Device.
"""

import glob
import os

from fpga.tool.ise import Ise
from fpga.tool.libero import Libero
from fpga.tool.quartus import Quartus
from fpga.tool.vivado import Vivado


class Project:
    """Manage an FPGA project."""

    def __init__(self, tool='vivado', part=None, project=None):
        """Instantiate the Tool to use."""
        if tool == 'ise':
            self.tool = Ise(project, part)
        elif tool == 'libero':
            self.tool = Libero(project, part)
        elif tool == 'quartus':
            self.tool = Quartus(project, part)
        elif tool == 'vivado':
            self.tool = Vivado(project, part)
        else:
            raise NotImplementedError(tool)
        self.outdir = 'build'

    def get_config(self):
        """Get the Project Configurations."""
        return self.tool.get_config()

    def set_outdir(self, outdir):
        """Set the OUTput DIRectory."""
        self.outdir = outdir

    def add_files(self, pathname, lib=None):
        """Add files to the project.

        PATHNAME must be a string containing an absolute or relative path
        specification, and can contain shell-style wildcards.
        LIB is optional and only useful for VHDL files.
        """
        path = os.getcwd()
        files = glob.glob(pathname)
        for file in files:
            file_abs = os.path.join(path, file)
            self.tool.add_file(file_abs, lib)

    def set_top(self, toplevel):
        """Set the TOP LEVEL of the project."""
        self.tool.set_top(toplevel)

    def set_strategy(self, strategy):
        """Set the Optimization STRATEGY."""
        self.tool.set_strategy(strategy)

    def set_task(self, task):
        """Set the TASK to reach when the Tool is executed."""
        self.tool.set_task(task)

    def set_project_opts(self, options):
        """Set project OPTIONS."""
        self.tool.set_options(options, 'project')

    def set_pre_flow_opts(self, options):
        """Set pre flow OPTIONS."""
        self.tool.set_options(options, 'pre-flow')

    def set_post_syn_opts(self, options):
        """Set post synthesis OPTIONS."""
        self.tool.set_options(options, 'post-syn')

    def set_post_imp_opts(self, options):
        """Set post implementation OPTIONS."""
        self.tool.set_options(options, 'post-imp')

    def set_post_bit_opts(self, options):
        """Set post bitstream generation OPTIONS."""
        self.tool.set_options(options, 'post-bit')

    def _run_in_other_dir(self, funcname):
        """Run a function in other directory."""
        prevdir = os.getcwd()
        nextdir = os.path.join(prevdir, self.outdir)
        try:
            if not os.path.exists(nextdir):
                os.mkdir(nextdir)
            os.chdir(nextdir)
            funcname()
        finally:
            os.chdir(prevdir)

    def generate(self):
        """Run the FPGA tool."""
        self._run_in_other_dir(self.tool.generate)

    def set_hard(self, devtype, position, name, width):
        """Set hardware configurations for the programmer."""
        self.tool.set_hard(devtype, position, name, width)

    def transfer(self):
        """Transfer a bitstream."""
        self._run_in_other_dir(self.tool.transfer)
