#!/bin/bash

set -e

BOARDS=("zybo" "arty")
SOURCES=("vlog" "vhdl" "slog")

for BOARD in "${BOARDS[@]}"; do
  for SOURCE in "${SOURCES[@]}"; do
    echo "> $BOARD - $SOURCE"
    python3 run.py --board $BOARD --source $SOURCE
  done
done
