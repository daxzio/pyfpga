# PyFPGA [![License](https://img.shields.io/badge/License-GPL--3.0-darkgreen?style=flat-square)](LICENSE)

![Diamond](https://img.shields.io/badge/Diamond-3.13-blue.svg?style=flat-square)
![ISE](https://img.shields.io/badge/ISE-14.7-blue.svg?style=flat-square)
![Libero](https://img.shields.io/badge/Libero--Soc-2024.1-blue.svg?style=flat-square)
![Quartus](https://img.shields.io/badge/Quartus--Prime-23.1-blue.svg?style=flat-square)
![Vivado](https://img.shields.io/badge/Vivado-2022.1-blue.svg?style=flat-square)

![Openflow](https://img.shields.io/badge/Openflow-GHDL%20%7C%20Yosys%20%7C%20nextpnr%20%7C%20icestorm%20%7C%20prjtrellis-darkgreen.svg?style=flat-square)

PyFPGA is an abstraction layer for working with FPGA development tools in a vendor-agnostic, programmatic way. It is a Python package that provides:
* One **class** per supported tool for **project creation**, **synthesis**, **place and route**, **bitstream generation**, and **programming**.
* A set of **command-line helpers** for simple projects or quick evaluations.

With PyFPGA, you can create your own FPGA development workflow tailored to your needs!

Some of its benefits are:
* It provides a unified API between tools/devices.
* It's **Version Control Systems** and **Continuous Integration** friendly.
* It ensures reproducibility and repeatability.
* It consumes fewer system resources than GUI-based workflows.

## Basic example

```py
from pyfpga import Vivado

prj = Vivado('example')
prj.set_part('xc7z010-1-clg400')
prj.add_vlog('location1/*.v')
prj.add_vlog('location2/top.v')
prj.add_cons('location3/example.xdc')
prj.set_top('Top')
prj.make()
```

The next steps are to read the [docs](https://pyfpga.github.io/pyfpga) or take a look at [examples](examples).

## Support

PyFPGA is a Python package developed having GNU/Linux platform on mind, but it should run well on any POSIX-compatible OS, and probably others!
If you encounter compatibility issues, please inform us via the [issues](https://github.com/PyFPGA/pyfpga/issues) tracker.

For a comprehensive list of supported tools, features and limitations, please refer to the [tools support](https://pyfpga.github.io/pyfpga/tools.html) page.

> **NOTE:**
> PyFPGA assumes that the underlying tools required for operation are ready to be executed from the running terminal.
> This includes having the tools installed, properly configured and licensed (when needed).

## Installation

> **NOTE:** PyFPGA requires Python >= 3.8.

PyFPGA can be installed in several ways:

1. From PyPi using pip:

```
pip install pyfpga
```

2. From the GitHub repository:

```
pip install 'git+https://github.com/PyFPGA/pyfpga#egg=pyfpga'
```

3. Clone/download the repository and install it manually:

```
git clone https://github.com/PyFPGA/pyfpga.git
cd pyfpga
pip install -e .
```

> **NOTE:** with `-e` (`--editable`), the application is installed into site-packages via a symlink, which allows you to pull changes through git or switch branches without reinstalling the package.

## Similar projects

* [edalize](https://github.com/olofk/edalize): an abstraction library for interfacing EDA tools.
* Firmware Framework ([FWK](https://gitlab.desy.de/fpgafw/fwk)): set of scripts and functions/procedures that combine all the input files needed to produce build.
* HDL On Git ([Hog](https://gitlab.com/hog-cern/Hog)): a set of Tcl/Shell scripts plus a suitable methodology to handle HDL designs in a GitLab repository.
* [Hdlmake](https://ohwr.org/project/hdl-make): tool for generating multi-purpose makefiles for FPGA projects.
* IPbus Builder ([IPBB](https://github.com/ipbus/ipbb)): a tool for streamlining the synthesis, implementation and simulation of modular firmware projects over multiple platforms.
* [tsfpga](https://github.com/tsfpga/tsfpga): a flexible and scalable development platform for modern FPGA projects.
