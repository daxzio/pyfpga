#!/bin/bash

set -e

HDIR=../../pyfpga/helpers

python3 $HDIR/hdl2bit.py -t gowin_yosys -o results/gowin_yosys-vlog -p GW2AR-LV18QN88C8/I7 \
    -i ../sources/vlog/include1 -i ../sources/vlog/include2 \
    -f ../sources/vlog/blink.v -f ../sources/vlog/top.v \
    -f ../sources/cons/tangnano20k/clk.nextpnr.cst \
    -f ../sources/cons/tangnano20k/led.nextpnr.cst \
    --define DEFINE1 1 --define DEFINE2 1 --param FREQ 27000000 --param SECS 1 Top

python3 $HDIR/hdl2bit.py -t gowin_yosys -o results/gowin_yosys-vhdl -p GW2AR-LV18QN88C8/I7 --project example \
    -f ../sources/vhdl/blink.vhdl,blink_lib -f ../sources/vhdl/blink_pkg.vhdl,blink_lib -f ../sources/vhdl/top.vhdl \
    -f ../sources/cons/tangnano20k/clk.nextpnr.cst \
    -f ../sources/cons/tangnano20k/led.nextpnr.cst \
    --param FREQ 27000000 --param SECS 1 --last syn Top

# Gowin Yosys has no vendor project file, so it is not supported by prj2bit

python3 $HDIR/bitprog.py -t gowin_yosys results/gowin_yosys-vlog/gowin_yosys.fs
